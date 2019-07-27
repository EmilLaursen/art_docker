# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime

class FinansSpider(scrapy.Spider):
    name = 'finans'
    allowed_domains = ['finans.dk']
    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        # The maximum download delay to be set in case of high latencies
        'AUTOTHROTTLE_MAX_DELAY': 60,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0,
        # Enable showing throttling stats for every response received:
        'AUTOTHROTTLE_DEBUG': True,
        'LOG_FILE': 'data/logs/finans.log',
    }


    # Use from crawler ? how to instantiate ?

    scrape_date = ''
    def start_requests(self):
        urls = ['http://www.finans.dk/']
        
        self.start_page_links = '.artRelLink::attr(href) , .baronContainer a::attr(href) , .artHd::attr(href)'
        self.article_links = '.artHd a::attr(href) , .artRelatedColumnCnt a::attr(href)'
        self.paywall_css = 'artViewLock__subscribe__erv'
        self.authors_css = '.popupCaller::text'
        self.alt_authors_css = '.bylineArt p::text'
        self.date_css = '.artTime::text'
        self.section_css = '.artSec::text'
        self.title_css = 'h1::text'
        self.sub_title_css= '.artManchet::text'
        self.body_css = '.artBody p'


        save_path = 'data/finans.jl'
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

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_startpage, meta={'dont_cache': True})

    def parse_startpage(self, response):
        for next_page in response.css(self.start_page_links).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse(self, response):
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('authors', self.authors_css)
        l.add_css('alt_authors', self.alt_authors_css)
        l.add_css('date', self.date_css)
        l.add_css('paywall', self.paywall_css)
        l.add_value('url', response.url)
        l.add_css('section', self.section_css)
        l.add_css('title', self.title_css)
        l.add_css('sub_title', self.sub_title_css)
        l.add_css('body', self.body_css)
        l.add_value('scrape_date', datetime.now())
        yield l.load_item()

        for next_page in response.css(self.article_links).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
