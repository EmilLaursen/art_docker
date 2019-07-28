# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime
from itertools import chain
from pathlib import Path

from scrapy.spiders import SitemapSpider

class DrSpider(SitemapSpider):
    name = 'drspider'
    sitemap_urls = [
        'https://www.dr.dk/sitemap.dr.dk3.xml',
        'https://www.dr.dk/sitemap.dr.dk.xml',
        'https://www.dr.dk/sitemap.dr.dk1.xml',
    ]
    sitemap_follow = ['/sitemap.dr']

    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        # The maximum download delay to be set in case of high latencies
        'AUTOTHROTTLE_MAX_DELAY': 60,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0,
        # Enable showing throttling stats for every response received:
        'AUTOTHROTTLE_DEBUG': True,

        'LOG_FILE': 'data/logs/dr.log',

        'JOBDIR' : 'data/' + name,
    }

    def __init__(self, category=None, *args, **kwargs):
        super(DrSpider, self).__init__(*args, **kwargs)
        
        save_path = 'data/dr.jl'
        self.scraped_urls = set()
        try:
            with open(save_path, mode='r') as reader:
                lines = reader.readlines()
                for line in lines:
                    dic = json.loads(line)
                    url = dic['url'][0]
                    self.scraped_urls.add(url)
        except FileNotFoundError:
            self.logger.info('{} not found'.format(save_path))
        self.logger.info('Found {} scraped pages.'.format(len(self.scraped_urls)))

        self.title_css = '.dre-article-title__title::text'
        self.section_css = '.dre-section-label__title--link::text'
        self.authors_css = '.dre-article-byline__author span::text'
        self.sub_title_css= '.dre-article-title__summary::text'
        self.date_css = '.dre-article-byline__date::text'
        #self.paywall_css = ''
        #self.alt_authors_css = ''
        self.body_css = '.dre-article-body__paragraph'

    def start_requests(self): # Ad-hoc hack to add the broken sitemap.
        other_urls = []
        url_file = 'data/www.dr.dk_sitemap.dr.dk2.txt'
        with open(url_file) as reader:
            for line in reader.readlines():
                other_urls.append(line)
        self.logger.info('Loaded {}'.format(url_file))
        primary_targets = super(DrSpider, self).start_requests()
        other_urls = (scrapy.Request(url) for url in other_urls)
        return chain(primary_targets, other_urls)

    def parse(self, response):
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('authors', self.authors_css)
        #l.add_css('alt_authors', self.alt_authors_css)
        l.add_css('date', self.date_css)
        l.add_value('paywall', 'premium' in response.url)
        l.add_value('url', response.url)
        l.add_css('section', self.section_css)
        l.add_css('title', self.title_css)
        l.add_css('sub_title', self.sub_title_css)
        l.add_css('body', self.body_css)
        l.add_value('scrape_date', datetime.now())
        yield l.load_item()