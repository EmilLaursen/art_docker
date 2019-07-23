# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions  import DropItem
import logging
from scrapy import logformatter


class ArtscraperPipeline(object):
    def process_item(self, item, spider):
        url = item.get('url', [])
        hsh = spider.md5(url[0]) if not url else ""
        if hsh in spider.scraped_url_hashes:
            spider.logger.info("Duplicate hash on item: {}".format(item['url']))
            raise DropItem()
        else:
            spider.scraped_url_hashes.add(hsh)
            return item


class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.DEBUG,
            'msg': logformatter.DROPPEDMSG,
            'args': {
                'exception': exception,
                'item': item,
            }
        }