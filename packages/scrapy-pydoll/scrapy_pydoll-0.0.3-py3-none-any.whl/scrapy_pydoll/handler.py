import asyncio
from functools import partial
import time
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from scrapy.settings import Settings
from scrapy.crawler import Crawler
from scrapy.utils.reactor import verify_installed_reactor
from scrapy import signals, Spider
from pydoll.browser.chrome import Chrome, Options
from pydoll.browser.page import Page
from twisted.internet.defer import Deferred, inlineCallbacks
from scrapy.utils.defer import deferred_from_coro
from dataclasses import dataclass
from typing import Dict, Self, Optional
import logging
from scrapy.http import Request, Response
from scrapy.http.headers import Headers
from scrapy.responsetypes import responsetypes
from pydoll.events.fetch import FetchEvents
from pydoll.commands.fetch import FetchCommands

from scrapy_pydoll.page import PageMethod
from scrapy_pydoll._utils import _encode_body, _maybe_await

__all__ = ["PydollDownloadHandler"]

logger = logging.getLogger("scrapy-pydoll")
logging.getLogger("websockets.client").setLevel(logging.WARNING)
logging.getLogger("pydoll").setLevel(logging.WARNING)
logging.getLogger("pydoll.connection.connection").setLevel(logging.WARNING)



@dataclass
class Config:
    headless: bool
    proxy: str
    max_pages: Optional[int]
    navigation_timeout: Optional[int]
    pydoll_abort_request: Optional[str]
    target_closed_max_retries: int = 3

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        return cls(
            headless=settings.get("PYDOLL_HEADLESS", True),
            proxy=settings.get("PYDOLL_PROXY", None),
            max_pages=settings.getint("PYDOLL_MAX_PAGES", 4),
            navigation_timeout=settings.getint("PYDOLL_NAVIGATION_TIMEOUT", 30),
            pydoll_abort_request=settings.get("PYDOLL_ABORT_REQUEST"),
        )



class PydollDownloadHandler(HTTPDownloadHandler):
    browser: Chrome = None


    def __init__(self, crawler: Crawler) -> None:
        super().__init__(crawler.settings, crawler)
        verify_installed_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
        crawler.signals.connect(self._engine_started, signal=signals.engine_started)
        self.stats = crawler.stats
        self.config = Config.from_settings(crawler.settings)
        self.page_semaphore = asyncio.Semaphore(self.config.max_pages)


    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler)


    def _engine_started(self) -> Deferred:
        """Launch browser when engine starts"""
        return deferred_from_coro(self._launch())


    async def interceptor(self, spider: Spider, page: Page, event: Dict) -> None:
        try:
            req_id = event['params']['requestId']
            req_url = event['params']['request']['url']
            req_method = event['params']['request']['method']
            await page._execute_command(
                FetchCommands.fail_request(
                    request_id=req_id,
                    error_reason="Aborted"
                )
            )
            logger.debug(
                "Aborted Pydoll request <%s %s>",
                req_method.upper(),
                req_url,
                extra={
                    "spider": spider,
                },
            )
            self.stats.inc_value("pydoll/request_count/aborted")
        except Exception as ex:
            logger.error(
                "Failed to abort request: %s exc_type=%s exc_msg=%s",
                event,
                type(ex),
                str(ex),
                extra={
                    "spider": spider,
                    "exception": ex,
                },
                exc_info=True,
            )
            await page._execute_command(
                FetchCommands.continue_request(
                    request_id=req_id,
                )
            )


    async def _launch(self) -> None:
        """Launch browser"""
        logger.info("Starting download handler")
        options = Options()
        if self.config.proxy:
            options.add_argument(f"--proxy-server={self.config.proxy}")
        if self.config.headless:
            options.add_argument("--headless")
        self.browser = Chrome(options=options)
        await self.browser.start()


    def download_request(self, request: Request, spider: Spider) -> Deferred:
        if request.meta.get("pydoll"):
            return deferred_from_coro(self._download_request(request, spider))
        return super().download_request(request, spider)
    

    async def _create_page(self, request: Request, spider: Spider) -> Page:
        page_id = await self.browser.new_page()
        page = await self.browser.get_page_by_id(page_id)
        if self.config.pydoll_abort_request:
            await page.enable_fetch_events(resource_type=self.config.pydoll_abort_request.title())
            await page.on(FetchEvents.REQUEST_PAUSED, partial(self.interceptor, spider, page))

        _total_page_count = await self._get_total_page_count()
        self.stats.set_value("pydoll/page_count", _total_page_count)
        logger.debug(
            "New page created, page count is %i",
            _total_page_count,
            extra={
                "spider": spider,
                "total_page_count": _total_page_count,
                "scrapy_request_url": request.url,
                "scrapy_request_method": request.method,
            },
        )
        await self._set_max_concurrent_page_count()
        return page


    async def _download_request(self, request: Request, spider: Spider) -> Response:
        page_acquired = False
        try:
            page: Page = request.meta.get("pydoll_page")
            if not isinstance(page, Page):
                await self.page_semaphore.acquire()
                page_acquired = True
                page = await self._create_page(request, spider)
            if request.meta.get("pydoll_include_page"):
                request.meta["pydoll_page"] = page

            start_time = time.time()
            await page.go_to(request.url, timeout=self.config.navigation_timeout)
            await self._apply_page_methods(page, request, spider)
            body_str = await page.page_source
            page_url = await page.current_url
            request.meta["download_latency"] = time.time() - start_time

            if not request.meta.get("pydoll_include_page"):
                await page.close()
            self.stats.inc_value("pydoll/page_count/closed")
            
            headers = Headers()
            body, encoding = _encode_body(headers=headers, text=body_str)
            respcls = responsetypes.from_args(headers=headers, url=page_url, body=body)
        except Exception as ex:
            respcls = None
            if not request.meta.get("pydoll_include_page"):
                logger.warning(
                    "Closing page due to failed request: %s exc_type=%s exc_msg=%s",
                    request,
                    type(ex),
                    str(ex),
                    extra={
                        "spider": spider,
                        "scrapy_request_url": request.url,
                        "scrapy_request_method": request.method,
                        "exception": ex,
                    },
                    exc_info=True,
                )
                await page.close()
                self.stats.inc_value("pydoll/page_count/closed")
            raise
        finally:
            if page_acquired:
                self.page_semaphore.release()
            if respcls:
                return respcls(
                    url=page_url,
                    status=200,
                    headers=headers,
                    body=body,
                    request=request,
                    flags=["pydoll"],
                    encoding=encoding,
                    ip_address=None,
                )


    async def _apply_page_methods(self, page: Page, request: Request, spider: Spider) -> None:
        page_methods = request.meta.get("pydoll_page_methods") or ()
        if isinstance(page_methods, dict):
            page_methods = page_methods.values()
        for pm in page_methods:
            if isinstance(pm, PageMethod):
                try:
                    if callable(pm.method):
                        method = partial(pm.method, page)
                    else:
                        method = getattr(page, pm.method)
                except AttributeError as ex:
                    logger.warning(
                        "Ignoring %r: could not find method",
                        pm,
                        extra={
                            "spider": spider,
                            "scrapy_request_url": request.url,
                            "scrapy_request_method": request.method,
                            "exception": ex,
                        },
                        exc_info=True,
                    )
                else:
                    pm.result = await _maybe_await(method(*pm.args, **pm.kwargs))
                    await page._wait_page_load(self.config.navigation_timeout)
            else:
                logger.warning(
                    "Ignoring %r: expected PageMethod, got %r",
                    pm,
                    type(pm),
                    extra={
                        "spider": spider,
                        "scrapy_request_url": request.url,
                        "scrapy_request_method": request.method,
                    },
                )


    async def _get_total_page_count(self) -> int:
        _targets = await self.browser.get_targets()
        targets = []
        for _target in _targets:
            if _target["type"] == "page" and _target['url'] != "about:blank":
                targets.append(_target)
        return len(targets)
    

    async def _set_max_concurrent_page_count(self):
        count = await self._get_total_page_count()
        current_max_count = self.stats.get_value("pydoll/page_count/max_concurrent")
        if current_max_count is None or count > current_max_count:
            self.stats.set_value("pydoll/page_count/max_concurrent", count)


    @inlineCallbacks
    def close(self) -> Deferred:
        logger.info("Closing download handler")
        yield super().close()
        yield deferred_from_coro(self._close())


    async def _close(self) -> None:
        if hasattr(self, "browser") and self.browser:
            logger.info("Closing browser")
            await self.browser.stop()