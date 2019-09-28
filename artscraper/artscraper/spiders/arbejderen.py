# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, unquote

class ArbejderenSpider(scrapy.Spider):
    name = 'arbejderen'
    allowed_domains = ['arbejderen.dk']
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

        'LOG_FILE': 'data/logs/arbejderen.log',

        #'JOBDIR' : 'data/' + name,

        'VISITED_FILTER_PATH' : 'data/arbejderen.filter',
        'LOG_LEVEL' : 'INFO',
    }

    def __init__(self, category=None, *args, **kwargs):
        super(ArbejderenSpider, self).__init__(*args, **kwargs)

        self.start_page_links = 'h1 a::attr(href)' #
        self.article_links = '.views-row div a::attr(href)' #
        self.paywall_css = '.pane-block-10' # 
        self.authors_css = '.skribenttitel::text' #
        self.alt_authors_css = '#page-aside-beta .views-row-last span::text' #
        self.date_css = '.created::text' #
        # self.section_css = ''
        self.title_css = '.pane-page-title h1::text' #
        self.sub_title_css= '.manchet, .manchetOld::text' #
        self.body_css = '.even p' #
        """ 
        save_path = 'data/arbejderen.jl'
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
            'http://www.arbejderen.dk/',
            'https://arbejderen.dk/blogs',
            'https://arbejderen.dk/arbejde-og-kapital',
            'https://arbejderen.dk/idekamp',
            'https://arbejderen.dk/kultur',
            'https://arbejderen.dk/indland',
            'https://arbejderen.dk/udland',
            'https://arbejderen.dk/marx',
            'https://arbejderen.dk/teori',
            'https://arbejderen.dk/s-regering',
            'https://arbejderen.dk/ok20',
            'https://arbejderen.dk/ghettolov',
            'https://arbejderen.dk/livsstil',
            'https://arbejderen.dk/v%C3%A5benindustri',
            'https://arbejderen.dk/social-dumping',
            'https://arbejderen.dk/tags/eu-modstand',
            'https://arbejderen.dk/krig',
            'https://arbejderen.dk/kalender',
            'https://arbejderen.dk/navne',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_startpage, meta={'dont_cache': True})

    def parse_startpage(self, response):
        link_css = '.field-content a::attr(href)' if 'blogs' in response.url else self.start_page_links
        self.logger.info(f'blogs in response.url? {"blogs" in response.url}. Response: {response.url}')
        for next_page in response.css(link_css).getall():
            if next_page is not None:
                parser = self.parse_blog if self.is_blog_url(next_page) else self.parse
                yield response.follow(next_page, callback=parser)

    def parse(self, response):
        self.logger.info(f'Parsing reponse {urlsplit(response.url).path}')
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('authors', self.authors_css)
        l.add_css('alt_authors', self.alt_authors_css)
        l.add_css('date', self.date_css)
        l.add_css('paywall', self.paywall_css)
        l.add_value('url', response.url)

        l.add_value('section', self._get_section(response.url))
        l.add_css('title', self.title_css)
        l.add_css('sub_title', self.sub_title_css)
        l.add_css('body', self.body_css)
        l.add_value('scrape_date', datetime.now())
        yield l.load_item()

        for next_page in response.css(self.article_links).getall():
            if next_page is not None:
                parser = self.parse_blog if self.is_blog_url(next_page) else self.parse
                yield response.follow(next_page, callback=parser)
    
    def parse_blog(self, response):
        self.logger.info(f'Parsing reponse {urlsplit(response.url).path}')
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('authors', '.views-row-first.views-row-last .views-field-name .field-content::text')
        l.add_css('date', '.pane-node-created .pane-content::text')
        l.add_value('paywall', False)
        l.add_value('url', response.url)
        
        l.add_value('section', self._get_section(response.url))

        l.add_css('title', 'h1::text')
        l.add_css('sub_title', '.manchet::text')
        l.add_css('body', '.pane-node-body p')
        l.add_value('scrape_date', datetime.now())
        yield l.load_item()

        for next_page in response.css('.field-content a::attr(href)').getall():
            if next_page is not None:
                parser = self.parse_blog if self.is_blog_url(next_page) else self.parse
                yield response.follow(next_page, callback=parser)

    def is_blog_url(self, url):
        return self._get_section(url) == 'blog-indlæg' or self._get_section(url) == 'blog-indl%C3%A6g'

    def _get_section(self, url):
        splitpath = urlsplit(url).path.split(sep='/')
        section = splitpath[1] if len(splitpath) >= 1 else None
        return unquote(section)