import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NewssiteFrontpageSpider(scrapy.Spider):
    name = "empty_newssite_spider"

    def __init__(self, category=None, *args, **kwargs):
        super(NewssiteFrontpageSpider, self).__init__(*args, **kwargs)

        # Subclass specific settings should be passed along in this key.
        cfg = kwargs.get("newssite")

        if cfg:
            self.startpage_links = cfg.get("startpage_links")
            self.startpage_follow_css = cfg.get("startpage_follow_css")
            self.article_follow_css = cfg.get("article_follow_css")
            self.paywall_css = cfg.get("paywall_css")
            self.authors_css = cfg.get("authors_css")
            self.alt_authors_css = cfg.get("alt_authors_css")
            self.date_css = cfg.get("date_css")
            self.title_css = cfg.get("title_css")
            self.sub_title_css = cfg.get("sub_title_css")
            self.body_css = cfg.get("body_css")
            self.section_css = cfg.get("section")
            self.predicate_loader_pairs = cfg.get("predicate_loader_pairs", [])
        else:
            raise NotImplementedError(f"newssite config not found")

    def start_requests(self):
        for url in self.startpage_links:
            yield scrapy.Request(
                # The "dont_cache" is used by job persistence middleware
                url=url,
                callback=self.parse_startpage,
                meta={"dont_cache": True},
            )

    def parse_startpage(self, response):
        follow_css = self.choose_follow_css(response)

        next_pages = response.css(follow_css).getall()
        logger.info(f"Parsing startpage: {response}, found links: {len(next_pages)}")

        for next_page in next_pages:
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def choose_follow_css(self, response):
        if response.url in self.startpage_links:
            return self.startpage_follow_css
        return self.article_follow_css

    def default_itemloader(self, response):
        loader = ItemLoader(item=ArtscraperItem(), response=response)
        # Item metadata.
        loader.add_value("scrape_date", datetime.now())
        loader.add_value("url", response.url)
        # Item css selectors, supplied by subclasses
        loader.add_css("date", self.date_css)
        loader.add_css("paywall", self.paywall_css)
        loader.add_css("authors", self.authors_css)
        loader.add_css("alt_authors", self.alt_authors_css)
        loader.add_css("title", self.title_css)
        loader.add_css("sub_title", self.sub_title_css)
        loader.add_css("section", self.section_css)
        loader.add_css("body", self.body_css)

        return loader

    def parse(self, response):
        # Prepare default item parse logic
        loader = self.default_itemloader(response)

        # Check if any custom parsing logic is needed for this response.
        custom_loaders = [
            custom_itemloader
            for (pred, custom_itemloader) in self.predicate_loader_pairs
            if pred(response)
        ]

        for itemloader in custom_loaders:
            loader = itemloader(loader, response)

        yield loader.load_item()

        follow_css = self.choose_follow_css(response)
        if follow_css:
            next_pages = response.css(follow_css).getall()
            logger.info(f"Parsing article page: {response}, Found links {len(next_pages)}")
            for next_page in next_pages:
                if next_page is not None:
                    yield response.follow(next_page, callback=self.parse)
        else:
            logger.info(f"Parsing article page: {response}")
