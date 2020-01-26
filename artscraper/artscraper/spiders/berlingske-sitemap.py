# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime
from itertools import chain
from pathlib import Path

from scrapy.spiders import SitemapSpider


class BerlingskeSitemapScraper(SitemapSpider):
    name = "bt_sitemap"
    sitemap_urls = ["https://www.berlingske.dk/sitemap.xml"]
    sitemap_follow = ["sitemap.xml/articles"]

    custom_settings = {
        "BOT_NAME": name,
        "LOG_FILE": "data/logs/berlingske-sitemap.log",
        "JOBDIR": "data/" + name,
        "VISITED_FILTER_PATH": "data/bt_sitemap.filter",
    }

    def __init__(self, category=None, *args, **kwargs):
        super(BerlingskeSitemapScraper, self).__init__(*args, **kwargs)

    def parse(self, response):
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

        for next_page in response.css(".teaser__title-link::attr(href)").getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
