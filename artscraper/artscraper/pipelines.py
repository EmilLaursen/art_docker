# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions  import DropItem
import logging
from scrapy import logformatter
from urllib.parse import urlparse

class ArtscraperPipeline(object):
    def process_item(self, item, spider):
        url = item['url'][0]
        if url in spider.scraped_urls:
            spider.logger.info("Duplicate on item: {}".format(urlparse(url).path))
            raise DropItem()
        else:
            spider.scraped_urls.add(url)
            return item


class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.DEBUG,
            'msg': logformatter.DROPPEDMSG,
            'args': {
                'exception': exception,
                'item': item.get('url', ''),
            }
        }