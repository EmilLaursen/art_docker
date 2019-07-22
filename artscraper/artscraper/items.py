# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose




class ArtscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    authors = scrapy.Field(
        input_processor=MapCompose(str.strip)
    )
    section = scrapy.Field(
        input_processor=MapCompose(str.strip)
    )
    alt_authors = scrapy.Field(
        input_processor=MapCompose(str.strip)
    )
    date = scrapy.Field(
        input_processor=MapCompose(str.strip)
    )
    url = scrapy.Field()
    title = scrapy.Field()
    sub_title = scrapy.Field()
    body = scrapy.Field()

