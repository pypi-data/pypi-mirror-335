from typing import Any, Callable, Dict, Iterable, Optional, Union

import scrapy
from pydantic import BaseModel, ConfigDict
from scrapy import Request
from scrapy.crawler import Crawler
from scrapy_poet import DummyResponse
from scrapy_spider_metadata import Args
from zyte_common_items import (
    ProbabilityRequest,
    ProductNavigation,
)

from zyte_spider_templates.params import parse_input_params
from zyte_spider_templates.spiders.base import (
    ARG_SETTING_PRIORITY,
    INPUT_GROUP,
    BaseSpider,
)
from zyte_spider_templates.utils import get_domain

from ..params import (
    ExtractFromParam,
    GeolocationParam,
    MaxRequestsParam,
    UrlParam,
    UrlsFileParam,
    UrlsParam,
)


class EcommerceNavigationSpiderParams(
    ExtractFromParam,
    MaxRequestsParam,
    GeolocationParam,
    UrlsFileParam,
    UrlsParam,
    UrlParam,
    BaseModel,
):
    model_config = ConfigDict(
        json_schema_extra={
            "groups": [
                INPUT_GROUP,
            ],
        },
    )


class EcommerceNavigationSpider(
    Args[EcommerceNavigationSpiderParams], BaseSpider
):
    """Spider that focuses on navigation only, extracting category and pagination links
    from e-commerce websites.

    Users can override extraction methods if needed, using Scrapy page objects patterns
    the same way as in the current e-commerce template.
    """

    name = "ecommerce_navigation"

    metadata: Dict[str, Any] = {
        **BaseSpider.metadata,
        "title": "E-commerce Navigation",
        "description": "Template for spiders that extract navigation data from e-commerce websites.",
    }

    @classmethod
    def from_crawler(
        cls, crawler: Crawler, *args, **kwargs
    ) -> scrapy.Spider:
        spider = super(EcommerceNavigationSpider, cls).from_crawler(
            crawler, *args, **kwargs
        )
        parse_input_params(spider)
        spider._init_extract_from()
        return spider

    def _init_extract_from(self):
        if self.args.extract_from is not None:
            self.settings.set(
                "ZYTE_API_PROVIDER_PARAMS",
                {
                    "productNavigationOptions": {
                        "extractFrom": self.args.extract_from
                    },
                    **self.settings.get("ZYTE_API_PROVIDER_PARAMS", {}),
                },
                priority=ARG_SETTING_PRIORITY,
            )

    def get_start_request(self, url):
        callback = self.parse_navigation
        meta = {
            "crawling_logs": {"page_type": "productNavigation"},
        }

        return Request(
            url=url,
            callback=callback,
            meta=meta,
        )

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield self.get_start_request(url)

    def parse_navigation(
        self, response: DummyResponse, navigation: ProductNavigation
    ) -> Iterable[Union[Request, ProductNavigation]]:
        yield navigation

        if navigation.nextPage:
            yield self.get_nextpage_request(navigation.nextPage)

    def parse_navigation_no_yield(
        self, response: DummyResponse, navigation: ProductNavigation
    ) -> Iterable[ProductNavigation]:
        if navigation.nextPage:
            yield self.get_nextpage_request(navigation.nextPage)

    def get_parse_navigation_request(
        self,
        request: Union[ProbabilityRequest, Request],
        callback: Optional[Callable] = None,
        page_params: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        page_type: str = "productNavigation",
    ) -> scrapy.Request:
        callback = callback or self.parse_navigation

        return request.to_scrapy(
            callback=callback,
            priority=priority or 0,
            meta={
                "page_params": page_params or {},
                "crawling_logs": {
                    "name": request.name or "",
                    "probability": request.get_probability(),
                    "page_type": page_type,
                },
            },
        )

    def get_nextpage_request(
        self,
        request: Union[ProbabilityRequest, Request],
        callback: Optional[Callable] = None,
        page_params: Optional[Dict[str, Any]] = None,
    ):
        return self.get_parse_navigation_request(
            request,
            callback,
            page_params,
            self._NEXT_PAGE_PRIORITY,
            "nextPage",
        )