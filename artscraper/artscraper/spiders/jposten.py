# -*- coding: utf-8 -*-
import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
from datetime import datetime

class JpostenSpider(scrapy.Spider):
    name = 'jposten'
    allowed_domains = ['jyllands-posten.dk']
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        # The maximum download delay to be set in case of high latencies
        'AUTOTHROTTLE_MAX_DELAY': 60,
        # The average number of requests Scrapy should be sending in parallel to
        # each remote server
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 4.0,
        # Enable showing throttling stats for every response received:
        'AUTOTHROTTLE_DEBUG': True,
        'LOG_FILE': 'data/logs/jposten.log',
        'COOKIES_ENABLED': False,
    }


    # Use from crawler ? how to instantiate ?

    scrape_date = ''
    def start_requests(self):
        urls = ['https://jyllands-posten.dk/']
        self.start_page_links = '.default::attr(href) , .artListLatest__title a::attr(href) , .artRelLink a::attr(href) , .artTitle a::attr(href)'
        self.article_links = 'super-widget-view-four-col .ng-star-inserted::attr(href)'

        self.paywall_css = ''
        self.authors_css = '.artView__byline__author__name::text'
        self.alt_authors_css = '.bylineArt p::text'
        self.date_css = '.artView__top__info__time::text'
        self.section_css = '.itemInPath.ng-star-inserted::text'
        self.title_css = '.artView__top__info__title::text'
        self.sub_title_css= '.artView__top__info__desc::text'
        self.body_css = 'p'


        save_path = 'data/jposten.jl'
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

    def parse_blogpage(self, response):
        blog_authors = '.newBlogAuthorName'
        blog_title = 'h1'
        blog_subtitle = '.artDescription'
        blog_links = '.artTitle a::attr(href) , .blogarticle_new::attr(href)'
        blog_section = 'blog'
        blog_date = '.artTime'

        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('date', blog_date)

        l.add_value('paywall', 'premium' in response.url)
        l.add_value('url', response.url)
        l.add_css('body', self.body_css)
        l.add_value('scrape_date', datetime.now())

        l.add_css('authors', blog_authors)
        l.add_css('title', blog_title)
        l.add_css('subtitle', blog_subtitle)
        l.add_value('section', blog_section)
        
        yield l.load_item()

        for next_page in response.css(blog_links).getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse_blogpage)
        
    def parse(self, response):
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('authors', self.authors_css)
        l.add_css('alt_authors', self.alt_authors_css)
        l.add_css('date', self.date_css)
        l.add_value('paywall', 'premium' in response.url)
        l.add_value('url', response.url)
        l.add_css('section', self.section_css)
        l.add_css('title', self.title_css)
        l.add_css('sub_title', self.sub_title_css)
        l.add_css('body', self.body_css)
        l.add_value('scrape_date', datetime.now())
        yield l.load_item()

        for next_page in response.css(self.article_links).getall():
            if next_page is not None:
                if 'debat/blog' in response.url:
                    yield response.follow(next_page, callback=self.parse_blogpage)
                else:
                    yield response.follow(next_page, callback=self.parse)
