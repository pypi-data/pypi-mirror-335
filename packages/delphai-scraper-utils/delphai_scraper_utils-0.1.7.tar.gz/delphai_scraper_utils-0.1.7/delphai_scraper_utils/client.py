import asyncio
import ssl
from typing import Any, Callable, List, Mapping, Union
from urllib.parse import urljoin, urlparse
from protego import Protego

from aiocache import cached
from httpx import (
    AsyncClient,
    ConnectError,
    ProxyError,
    ReadTimeout,
    RemoteProtocolError,
    TimeoutException,
)
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from httpx._config import (
    DEFAULT_LIMITS,
    DEFAULT_MAX_REDIRECTS,
    DEFAULT_TIMEOUT_CONFIG,
    Limits,
)
from httpx._models import Cookies, Response
from httpx._transports.base import AsyncBaseTransport
from httpx._types import (
    AuthTypes,
    CertTypes,
    CookieTypes,
    HeaderTypes,
    ProxiesTypes,
    QueryParamTypes,
    RequestContent,
    RequestData,
    RequestFiles,
    TimeoutTypes,
    URLTypes,
    VerifyTypes,
)
from tenacity import (
    AsyncRetrying,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from .metrics import request_timer

HTTP_RETRY_EXCEPTION_TYPES = (
    retry_if_exception_type(TimeoutException)
    | retry_if_exception_type(ConnectError)
    | retry_if_exception_type(ReadTimeout)
    | retry_if_exception_type(ProxyError)
    | retry_if_exception_type(RemoteProtocolError)
    | retry_if_exception_type(ssl.SSLZeroReturnError)
    | retry_if_exception_type(ssl.SSLError)
)


class TimeoutError(Exception):
    pass


class RobotFileParserTimeoutError(Exception):
    pass


class ScraperClient(AsyncClient):
    def __init__(
        self,
        *,
        auth: AuthTypes = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        verify: VerifyTypes = True,
        cert: CertTypes = None,
        http1: bool = True,
        http2: bool = False,
        proxies: ProxiesTypes = None,
        mounts: Mapping[str, AsyncBaseTransport] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
        follow_redirects: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        event_hooks: Mapping[str, List[Callable]] = None,
        base_url: URLTypes = "",
        transport: AsyncBaseTransport = None,
        app: Callable = None,
        trust_env: bool = True,
        persist_cookies: bool = False,
        scraper_id: Union[str, None] = None,
        max_retry_attempts: int = 3,
        retry_wait_multiplier: int = 1,
        retry_wait_max: int = 1,
        ignore_robots_txt: bool = False,
        robot_txt_retries: int = 3,
    ):
        super().__init__(
            auth=auth,
            params=params,
            headers=headers,
            cookies=cookies,
            verify=verify,
            cert=cert,
            http1=http1,
            http2=http2,
            proxies=proxies,
            mounts=mounts,
            timeout=timeout,
            follow_redirects=follow_redirects,
            limits=limits,
            max_redirects=max_redirects,
            event_hooks=event_hooks,
            base_url=base_url,
            transport=transport,
            app=app,
            trust_env=trust_env,
        )
        self.scraper_id = scraper_id
        self.persist_cookies = persist_cookies
        self.ignore_robots_txt = ignore_robots_txt
        self.robot_txt_retries = robot_txt_retries

        # Wrap request in retry decorator
        self.request = retry(
            stop=stop_after_attempt(max_retry_attempts),
            wait=wait_random_exponential(
                multiplier=retry_wait_multiplier, max=retry_wait_max
            ),
            retry=HTTP_RETRY_EXCEPTION_TYPES,
            reraise=True,
        )(self.request)

    async def request(
        self,
        method: str,
        url: URLTypes,
        *,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json: Any = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        auth: Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> Response:
        request = self.build_request(
            method=method,
            url=url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

        if not self.ignore_robots_txt:
            user_agent = request.headers.get("user-agent", "*")
            if not await self.is_allowed_by_robots_text(url, user_agent):
                return Response(403, request=request)

        if not self.persist_cookies:
            self._cookies = Cookies(None)
        with request_timer(scraper_id=self.scraper_id):
            return await self.send(
                request, auth=auth, follow_redirects=follow_redirects
            )

    @cached()
    async def get_robots_text_parser(self, base_url: str, user_agent: str) -> Protego:
        robots_text_url = urljoin(base_url, "robots.txt")
        robot_file_parser = Protego()

        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.robot_txt_retries),
            wait=wait_random_exponential(multiplier=1, max=10),
        ):
            with attempt:
                response = await super().request(
                    "GET",
                    robots_text_url,
                    headers={"user-agent": user_agent},
                    follow_redirects=True,
                )

        if response.status_code == 200:
            try:
                content = await asyncio.wait_for(
                    self.get_robots_txt_stream(response), timeout=5
                )
                await asyncio.get_running_loop().run_in_executor(
                    None, robot_file_parser.parse, content
                )
            except TimeoutError:
                raise RobotFileParserTimeoutError(
                    f"Timeout while parsing {robots_text_url}"
                )
        elif response.status_code in (401, 403):
            robot_file_parser.parse("User-agent: *\nDisallow: /")
        else:
            robot_file_parser.parse("User-agent: *\nAllow: /")

        return robot_file_parser

    async def get_robots_txt_stream(self, response, max_content_length=512000) -> str:
        """
        The Robots Exclusion Protocol requires crawlers to parse at least 500 kibibytes (512000 bytes)
        """
        content = []
        total_size = 0

        async for line in response.aiter_lines():
            line_size = len(line.encode())
            if total_size + line_size > max_content_length:
                break
            content.append(line)
            total_size += line_size

        return "\n".join(content)

    async def is_allowed_by_robots_text(self, url: str, user_agent: str) -> bool:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_text_parser = await self.get_robots_text_parser(base_url, user_agent)

        return robots_text_parser.can_fetch(url=url, user_agent=user_agent)
