from typing import Self
from rnet import Client, Response
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
from scrapy.crawler import Crawler
from scrapy.http import Headers, Request, Response
from scrapy.responsetypes import responsetypes
from scrapy.spiders import Spider
from scrapy.utils.defer import deferred_f_from_coro_f
from scrapy.utils.reactor import verify_installed_reactor
from twisted.internet.defer import Deferred

from scrapy_rnet.parser import RnetOptionsParser, RequestParser


class ImpersonateDownloadHandler(HTTPDownloadHandler):
    def __init__(self, crawler) -> None:
        settings = crawler.settings
        super().__init__(settings=settings, crawler=crawler)

        verify_installed_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler)

    def download_request(self, request: Request, spider: Spider) -> Deferred:
        if request.meta.get("impersonate"):
            return self._download_request(request, spider)
        return super().download_request(request, spider)

    @deferred_f_from_coro_f
    async def _download_request(self, request: Request, spider: Spider) -> Response:
        client = Client(
            **RnetOptionsParser(request).as_dict()
        )
        response: Response = await client.request(
            **RequestParser(request).as_dict()
        )
        content = await response.bytes()
        headers = Headers({key: val for key, val in response.headers.items()})
        headers.pop("Content-Encoding", None)

        respcls = responsetypes.from_args(
            headers=headers,
            url=response.url,
            body=content,
        )

        return respcls(
            url=response.url,
            status=response.status_code.as_int(),
            headers=headers,
            body=content,
            flags=["impersonate"],
            request=request,
        )