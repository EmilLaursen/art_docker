# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import logging
import datetime
import hashlib
import uuid
import sqlite3
from sqlite3 import Error
from urllib.parse import urlparse
import collections
from typing import Iterator, Optional, List

from scrapy.exceptions import DropItem
from scrapy import logformatter

logger = logging.getLogger(__name__)


class ArtscraperPipeline(object):
    def process_item(self, item, spider):
        url = item["url"][0]
        if hasattr(spider, "scraped_urls"):
            if url in spider.scraped_urls:
                spider.logger.info("Duplicate on item: {}".format(urlparse(url).path))
                raise DropItem()
            else:
                spider.scraped_urls.add(url)
        return item


class ScrapeStatsPersistancePipeline:
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS scrape_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scraper TEXT NOT NULL,
        scrape_date TEXT,
        total_scraped INTEGER NOT NULL ,
        date INTEGER NOT NULL,
        section INTEGER NOT NULL,
        authors INTEGER NOT NULL,
        alt_authors INTEGER NOT NULL,
        title INTEGER NOT NULL,
        sub_title INTEGER NOT NULL,
        body INTEGER NOT NULL,
        body_bytes INTEGER NOT NULL
    );
    """

    # TODO: include stats about scraped text size etc.
    def __init__(self, db_file):
        self.ordered_keys = [
            "total_scraped",
            "date",
            "section",
            "authors",
            "alt_authors",
            "title",
            "sub_title",
            "body",
        ]
        self.expected_keys = set(self.ordered_keys)
        self.scraped_field_counter = collections.Counter()

        self.db_file = db_file if db_file else "data/missing_stats.db"
        self.conn = None

    @classmethod
    def from_crawler(cls, crawler):
        db_file = crawler.settings.get("MISSING_STATS_DB_FILE")
        return cls(db_file)

    def open_spider(self, spider):
        try:
            self.conn = sqlite3.connect(self.db_file)
            logger.info(f"SQL Connection established: {sqlite3.version}")
        except Error as e:
            raise e

        # create table if it does not exist
        try:
            c = self.conn.cursor()
            c.execute(ScrapeStatsPersistancePipeline.CREATE_TABLE_SQL)
            c.close()
        except Error as e:
            raise e

    def close_spider(self, spider):
        self._write_data(spider)
        self.conn.close()

    def process_item(self, item, spider):
        present_keys = set(item.keys())
        missing_fields = [
            field
            for field in self.expected_keys
            if field not in present_keys or not item[field]
        ]
        # payload size.
        text = " ".join(item.get("body", []))
        body_bytes = len(text.encode("utf-8"))
        self.scraped_field_counter.update(missing_fields)
        self.scraped_field_counter["body_bytes"] += body_bytes
        return item

    def _write_data(self, spider):
        logger.info(f"Missing fields counter: {self.scraped_field_counter}")
        scraper = spider.name
        scrape_date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        row = (
            (scraper, scrape_date)
            + tuple(self.scraped_field_counter[field] for field in self.ordered_keys)
            + (self.scraped_field_counter["body_bytes"],)
        )

        sql = """
             INSERT INTO scrape_stats(scraper,scrape_date,total_scraped,date,section,authors,alt_authors,title,sub_title,body,body_bytes)
             VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """

        cur = self.conn.cursor()
        cur.execute(sql, row)
        self.conn.commit()
        cur.close()
        logger.info(f"inserted data into db. Last row id: {cur.lastrowid}")


def get_date(item):
    datetime_list = item.get("scrape_date", [""])
    dt = datetime_list[0]
    if type(dt) == str:
        date = dt[:10]
    elif isinstance(dt, datetime.datetime):
        date = dt.strftime("%Y-%m-%d")
    return date


class ContentHash:
    def process_item(self, item, spider):
        four_bytes = 4
        hash_func = hashlib.blake2b(digest_size=four_bytes)
        body = item.get("body")

        if body is None:
            logger.critical(f"Spider: {spider} got body of NoneType from url: {item.get('url')}")
            return item

        prefix = f"{spider.name[:5]}^{get_date(item)}^"

        if type(body) == list:
            for para in body:
                hash_func.update(para.encode("utf-8"))

        elif type(body) == str:
            hash_func.update(body.encode("utf-8"))
            logger.warning(f"{type(self)} recieved string body.")

        else:
            logger.critical(f"{type(self)} recieved body of type {type(body)}")
            item["uid"] = prefix + uuid.uuid4().hex[:6]
            return item

        item["uid"] = prefix + hash_func.hexdigest()
        return item

class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            "level": logging.DEBUG,
            "msg": logformatter.DROPPEDMSG,
            "args": {"exception": exception, "item": item.get("url", "")},
        }
