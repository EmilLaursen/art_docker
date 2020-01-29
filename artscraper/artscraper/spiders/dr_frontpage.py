# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime

from urllib.parse import urlsplit, unquote


class DrFrontpage(scrapy.Spider):
    name = "dr_frontpage_old"
    custom_settings = {
        "BOT_NAME": name,
        "DOWNLOAD_DELAY": 2,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 2,
        # The maximum download delay to be set in case of high latencies
        "AUTOTHROTTLE_MAX_DELAY": 60,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4.0,
        # Enable showing throttling stats for every response received:
        "AUTOTHROTTLE_DEBUG": False,
        "LOG_FILE": "data/logs/dr_frontpage.log",
        #'JOBDIR' : 'data/' + name,
        "VISITED_FILTER_PATH": "data/dr_frontpage.filter",
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, category=None, *args, **kwargs):
        super(DrFrontpage, self).__init__(*args, **kwargs)

        self.title_css = ".dre-article-title__title::text"
        self.section_css = ".dre-section-label__title--link::text"
        self.authors_css = ".dre-article-byline__author span::text"
        self.sub_title_css = ".dre-article-title__summary::text"
        self.date_css = ".dre-article-byline__date::text"
        # self.paywall_css = ''
        # self.alt_authors_css = ''
        self.body_css = ".dre-article-body__paragraph"
        self.start_page_links = ".heading-small a::attr(href)"

        # possible article_link css : .dre-teaser a

    def start_requests(self):  # Ad-hoc hack to add the broken sitemap.
        urls = [
            "https://www.dr.dk/nyheder/allenyheder/indland",
            "https://www.dr.dk/nyheder/allenyheder/udland",
            "https://www.dr.dk/nyheder/allenyheder/penge",
            "https://www.dr.dk/nyheder/allenyheder/politik",
            "https://www.dr.dk/nyheder/allenyheder/sporten",
            "https://www.dr.dk/nyheder/allenyheder/kultur",
            "https://www.dr.dk/nyheder/allenyheder/viden",
            "https://www.dr.dk/nyheder/allenyheder/mitliv",
            "https://www.dr.dk/nyheder/allenyheder/p4",
            "https://www.dr.dk/nyheder/allenyheder/vejret",
            "https://www.dr.dk/nyheder/allenyheder/",
        ]
        for url in urls:
            yield scrapy.Request(
                url=url, callback=self.parse_startpage, meta={"dont_cache": True}
            )

    def parse_startpage(self, response):
        for next_page in response.css(self.start_page_links).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse(self, response):
        self.logger.info(f"Parsing reponse {urlsplit(response.url).path}")
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css("authors", self.authors_css)
        # l.add_css('alt_authors', self.alt_authors_css)
        l.add_css("date", self.date_css)
        l.add_value("paywall", "premium" in response.url)
        l.add_value("url", response.url)
        l.add_css("section", self.section_css)
        l.add_css("title", self.title_css)
        l.add_css("sub_title", self.sub_title_css)
        l.add_css("body", self.body_css)
        l.add_value("scrape_date", datetime.now())
        yield l.load_item()
