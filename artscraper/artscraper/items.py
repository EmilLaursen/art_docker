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
import w3lib.html

short_month_map = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "ma": 3,
    "apr": 4,
    "maj": 5,
    "juni": 6,
    "jun": 6,
    "juli": 7,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "okt": 10,
    "nov": 11,
    "dec": 12,
}

month_map = {
    "januar": 1,
    "februar": 2,
    "marts": 3,
    "april": 4,
    "maj": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

DATE_REGEXES = {
    "BT_DATE_REGEX": re.compile(r"d. (\d+). (\w+) (\d{4}), kl. (\d+).(\d+)"),
    "DR_DATE_REGEX": re.compile(r"(\d{2}). (\w+). (\d{4}) kl. (\d{2}).(\d{2})"),
    "FINANS_DATE_REGEX": re.compile(r"(\d{2}).(\d{2}).(\d{4}) kl. (\d{2}).(\d{2})"),
    "KRISTELIGT_DATE_REGEX": re.compile(
        r"(\d{1,2}). (\w+) (\d{4}), kl. (\d{1,2}).(\d{2})"
    ),
    "ARBEJDEREN_DATE_REGEX": re.compile(
        r"(\d{2}). (\w+). (\d{4}),?(?: -)? (\d{1,2}):(\d{2})"
    ),
}


def parse_date_match(match, month_maps=[month_map]):
    day = int(match.group(1))

    # Try each month_map. If none works default use match group 2.
    for mmap in month_maps:
        if mmap.get(match.group(2)):
            month = mmap.get(match.group(2))
            break
    else:
        month = int(match.group(2))

    year = int(match.group(3))
    hour = int(match.group(4))
    minute = int(match.group(5))
    return year, month, day, hour, minute


def extract_datetime(date_string):

    for n, regex in DATE_REGEXES.items():
        match = re.search(regex, date_string)
        if match:
            return datetime(*parse_date_match(match, [month_map, short_month_map]))

    return date_string


def remove_section_garbage(xs):
    if len(xs) > 1:
        cleaner = (
            lambda y: "Abonnement" not in y
            and "Nyhedsvarsel" not in y
            and "Direkte" not in y
        )
        return remove_duplicates(filter(cleaner, xs))
    return xs


def remove_duplicates(xs):
    return list(set(xs))


def filter_empty(x):
    return x if x else None


class ArtscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    authors = Field(
        input_processor=MapCompose(w3lib.html.remove_tags, str.strip, filter_empty)
    )
    section = Field(
        input_processor=Compose(
            MapCompose(w3lib.html.remove_tags, str.strip, filter_empty),
            remove_section_garbage,
        )
    )
    alt_authors = Field(
        input_processor=MapCompose(w3lib.html.remove_tags, str.strip, filter_empty)
    )
    date = Field(input_processor=MapCompose(str.strip, filter_empty, extract_datetime))
    sub_title = Field(
        input_processor=MapCompose(w3lib.html.remove_tags, str.strip, filter_empty)
    )
    title = Field(
        input_processor=MapCompose(w3lib.html.remove_tags, str.strip, filter_empty)
    )
    paywall = Field(input_processor=MapCompose(w3lib.html.remove_tags))
    url = Field(input_processor=TakeFirst())
    body = Field(
        input_processor=MapCompose(w3lib.html.remove_tags, str.strip, filter_empty)
    )
    scrape_date = Field()
