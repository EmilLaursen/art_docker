import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
import hashlib
import logging

class BerlingskeScraper(scrapy.Spider):
    name = 'arts'
    allowed_domains = ['berlingske.dk']

    def start_requests(self):
        urls = [
            'https://www.berlingske.dk/business',
            'https://www.berlingske.dk/nyheder',
            'https://www.berlingske.dk/opinion',
            'https://www.berlingske.dk/aok',
        ]

        self.scraped_urls = set()
        try:
            with open('data/arts.jl', mode='r') as reader:
                for line in reader.readlines():
                    dic = json.loads(line)
                    url = dic['url'][0]
                    self.scraped_urls.add(url[0])
        except FileNotFoundError:
            pass
        self.logger.info('Found {} scraped pages.'.format(len(self.scraped_urls)))

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
