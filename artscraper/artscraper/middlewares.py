# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import NotConfigured, IgnoreRequest
from bloom_filter import BloomFilter
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ArtscraperSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class VisitedFilter(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, settings, stats):
        self.never_cache = set(
            urlparse(url).path for url in settings.get("NEVER_CACHE", [])
        )
        self.never_cache.add(urlparse("/robots.txt").path)

        logger.info(f"Initiating bloom filter.... Never Cache paths: {sorted(self.never_cache)}")

        self.visited = BloomFilter(
            max_elements=settings.getint("VISITED_FILTER_MAX_REQUESTS", 4000000),
            error_rate=settings.getfloat("VISITED_FILTER_ERROR_RATE", 1e-9),
            filename=settings.get("VISITED_FILTER_PATH"),
        )
        self.stats = stats
        logger.info(
            f"Loaded visited urls bloomfilter. Size {self.visited.num_bits_m / (1024 ** 2 * 8)} MiB."
        )

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.

        filter_path = crawler.settings.get("VISITED_FILTER_PATH", None)

        if not filter_path:
            logger.critical(f"VisitedFilter filter_path not configured !!")
            raise NotConfigured
        s = cls(crawler.settings, crawler.stats)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        url_path = urlparse(request.url).path
        if (
            url_path in self.visited
            and not request.meta.get("dont_cache", False)
            and url_path not in self.never_cache
        ):
            self.stats.inc_value("visited_filter/duplicate")
            logger.info(f"Request.url visited already: {url_path}")
            raise IgnoreRequest()
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        self.visited.add(urlparse(response.url).path)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self, spider):
        self.visited.backend.close()
        spider.logger.info(f"Closed bloomfilter {spider.name}")
