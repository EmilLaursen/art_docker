# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field
from scrapy.loader.processors import MapCompose, TakeFirst, Compose
from datetime import datetime
import re

month_map = {
    'januar': 1,
    'februar': 2,
    'marts': 3,
    'april': 4,
    'maj': 5,
    'juni': 6,
    'juli': 7,
    'august': 8,
    'september': 9,
    'oktober': 10,
    'november': 11,
    'december': 12,
}
date_regex = re.compile(r'd. (\d+). (\w+) (\d{4}), kl. (\d+).(\d+)')

def extract_datetime(date_string):
    m = re.search(date_regex, date_string)
    if m:
        day = int(m.group(1))
        month = month_map[m.group(2)]
        year = int(m.group(3))
        hour = int(m.group(4))
        minute = int(m.group(5))
        return datetime(year, month, day, hour, minute)
    return date_string

def remove_section_garbage(xs):
    if len(xs) > 1:
        cleaner = lambda y: 'Abonnement' not in y and 'Nyhedsvarsel' not in y and 'Direkte' not in y
        return remove_duplicates(filter(cleaner, xs))
    return xs

def remove_duplicates(xs):
    return list(set(xs))

class ArtscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    filter_empty = lambda x: x if x else None
    
    authors = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    section = Field(
        input_processor=Compose(MapCompose(str.strip, filter_empty), remove_section_garbage)
    )
    alt_authors = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    date = Field(
        input_processor=MapCompose(str.strip, filter_empty, extract_datetime)
    )
    sub_title = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    title = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    paywall = Field()
    url = Field(
        input_processor=TakeFirst()
    )
    body = Field(
        input_processor=MapCompose(str.strip, filter_empty)
    )
    scrape_date = Field()
