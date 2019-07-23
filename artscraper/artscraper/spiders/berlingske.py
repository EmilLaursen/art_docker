import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
import hashlib
import logging

class BerlingskeScraper(scrapy.Spider):
    name = 'arts'
    allowed_domains = ['berlingske.dk']
    
    def md5(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def start_requests(self):
        urls = [
            'https://www.berlingske.dk/business'
        ]
        self.scraped_url_hashes = set()
        try:
            with open('data/arts.jl', mode='r') as reader:
                for line in reader.readlines():
                    dic = json.loads(line)
                    url = dic.get('url', [])
                    hsh = self.md5(url[0]) if not url else ""
                    self.scraped_url_hashes.add(hsh)
        except FileNotFoundError:
            self.logger.info('JsonLines file not found.')
        

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        self.logger.info('Parsing: {}'.format(response.url))
        l = ItemLoader(item=ArtscraperItem(), response=response)
        l.add_css('authors', '.article-byline__author-name::text')
        l.add_css('alt_authors', '.font-g1::text')
        l.add_css('date', '.article-byline__date::text')
        l.add_value('url', response.url)
        l.add_css('section', '#articleHeader .d-inline-block::text')
        l.add_css('title', '.article-header__title::text')
        l.add_css('sub_title', '.article-header__intro::text')
        l.add_css('body', '#articleBody h2 , #articleBody p')
        yield l.load_item()

        for next_page in response.css('.teaser__title-link::attr(href)').getall():
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
