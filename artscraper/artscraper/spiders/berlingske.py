import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
from urllib.parse import urlsplit

from datetime import datetime


class BerlingskeScraper(scrapy.Spider):
    name = "berlingske_frontpage"
    allowed_domains = ["berlingske.dk"]
    custom_settings = {
        "BOT_NAME": name,
        "AUTOTHROTTLE_ENABLED": False,
        "AUTOTHROTTLE_START_DELAY": 1,
        # The maximum download delay to be set in case of high latencies
        "AUTOTHROTTLE_MAX_DELAY": 60,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 4.0,
        # Enable showing throttling stats for every response received:
        "AUTOTHROTTLE_DEBUG": False,
        "LOG_FILE": f"data/logs/{name}.log",
        "VISITED_FILTER_PATH": "data/bt_sitemap.filter",
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, category=None, *args, **kwargs):
        super(BerlingskeScraper, self).__init__(*args, **kwargs)

    def start_requests(self):
        urls = [
            "https://www.berlingske.dk/",
            "https://www.berlingske.dk/business",
            "https://www.berlingske.dk/nyheder",
            "https://www.berlingske.dk/opinion",
            "https://www.berlingske.dk/aok",
            "https://www.berlingske.dk/kommentarer",
            "https://www.berlingske.dk/oekonomi",
            "https://www.berlingske.dk/virksomheder",
            "https://www.berlingske.dk/karriere",
            "https://www.berlingske.dk/privatoekonomi",
            "https://www.berlingske.dk/business",
            "https://www.berlingske.dk/aktier",
            "https://www.berlingske.dk/usa/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.logger.info(f"Parsing reponse {urlsplit(response.url).path}")
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css("authors", ".article-byline__author-name::text")
        l.add_css("alt_authors", ".font-g1::text")
        l.add_css("date", ".article-byline__date::text")
        l.add_value("url", response.url)
        l.add_css("section", "#articleHeader .d-inline-block::text")
        l.add_css("title", ".article-header__title::text")
        l.add_css("sub_title", ".article-header__intro::text")
        l.add_css("body", "#articleBody h2 , #articleBody p")
        l.add_value("scrape_date", datetime.now())
        yield l.load_item()

        # frontpage is special with regards to following links.
        if response.url == "https://www.berlingske.dk/":
            href_css_selector = ".dre-item a::attr(href)"
        else:
            href_css_selector = ".teaser__title-link::attr(href)"

        for next_page in response.css(href_css_selector).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
