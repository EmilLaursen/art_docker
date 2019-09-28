# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, unquote

class KristeligtDagbladSpider(scrapy.Spider):
    name = 'kristeligt'
    allowed_domains = ['kristeligt-dagblad.dk']
    custom_settings = {
        'BOT_NAME' : name,
        'AUTOTHROTTLE_ENABLED': False,
        'AUTOTHROTTLE_START_DELAY': 1,
        # The maximum download delay to be set in case of high latencies
        'AUTOTHROTTLE_MAX_DELAY': 60,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0,
        # Enable showing throttling stats for every response received:
        'AUTOTHROTTLE_DEBUG': False,
        'LOG_FILE': 'data/logs/kristeligt.log',
        #'JOBDIR' : 'data/' + name,
        'VISITED_FILTER_PATH' : 'data/kristeligt.filter',
        'LOG_LEVEL' : 'INFO',
    }
    def __init__(self, category=None, *args, **kwargs):
        super(KristeligtDagbladSpider, self).__init__(*args, **kwargs)

        self.start_page_links = '.heading+ .column a::attr(href) , .related a::attr(href) , .heading a::attr(href)' 
        self.article_links = '.link::attr(href)'
        self.paywall_css = '.paid'
        self.authors_css = '.byline::text' 
        #self.alt_authors_css = '#page-aside-beta .views-row-last span::text' #
        self.date_css = '.publication::text' 
        #self.section_css = '.artSec::text' #
        self.title_css = '#new_recommendation+ .article h1::text' 
        self.sub_title_css= '.lead::text' 
        self.body_css = '#new_recommendation+ .article p' 

        """         save_path = 'data/kristeligt.jl'
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
        """

    def start_requests(self):
        urls = [
            'https://www.kristeligt-dagblad.dk/',
            'https://www.kristeligt-dagblad.dk/bagsiden/',
            'https://www.kristeligt-dagblad.dk/udland/',
            'https://www.kristeligt-dagblad.dk/danmark/',
            'https://www.kristeligt-dagblad.dk/liv-sjael/',
            'https://www.kristeligt-dagblad.dk/kronik/',
            'https://www.kristeligt-dagblad.dk/kirke',
            'https://www.kristeligt-dagblad.dk/kultur',

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_startpage, meta={'dont_cache': True})

    def parse_startpage(self, response):
        for next_page in response.css(self.start_page_links).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def parse(self, response):
        self.logger.info(f'Parsing reponse {urlsplit(response.url).path}')
        l = ItemLoader(item=ArtscraperItem(), response=response)
        
        #l.add_css('alt_authors', self.alt_authors_css)
        l.add_css('date', self.date_css)
        l.add_css('paywall', self.paywall_css)
        l.add_value('url', response.url)

        if self.is_debatindlaeg_url(response.url):
            body = response.css('#new_recommendation+ .article p::text').getall()
            author = body[0] if body else body
            l.add_value('authors', author)
        else:
            l.add_css('authors', self.authors_css)

        l.add_value('section', self._get_section(response.url))
        l.add_css('title', self.title_css)
        l.add_css('sub_title', self.sub_title_css)
        l.add_css('body', self.body_css)
        l.add_value('scrape_date', datetime.now())
        yield l.load_item()

        for next_page in response.css(self.article_links).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
    
    def is_debatindlaeg_url(self, url):
        return self._get_section(url) == 'debatindlaeg' # or self._get_section(url) == 'blog-indl%C3%A6g'

    def _get_section(self, url):
        splitpath = urlsplit(url).path.split(sep='/')
        section = splitpath[1] if len(splitpath) >= 1 else None
        return unquote(section)