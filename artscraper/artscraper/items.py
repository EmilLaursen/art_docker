# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field
from scrapy.loader.processors import MapCompose


class ArtscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    filter_empty = lambda x: x if x else None
    authors = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    section = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    alt_authors = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    date = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    sub_title = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    title = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    paywall = Field()
    url = Field()
    body = Field()
    scrape_date = Field()
