import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader
import json
import hashlib
import logging
from pathlib import Path

class BerlingskeScraper(scrapy.Spider):
    name = 'arts'
    allowed_domains = ['berlingske.dk']
    custom_settings = {
        'LOG_FILE': 'data/logs/berlingske.log',
        'JOBDIR' : 'data/' + name,
    }
    def __init__(self, category=None, *args, **kwargs):
        super(BerlingskeScraper, self).__init__(*args, **kwargs)
        
        save_path = 'data/arts.jl'
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

    def start_requests(self):
        urls = [
            'https://www.berlingske.dk/',
            'https://www.berlingske.dk/business',
            'https://www.berlingske.dk/nyheder',
            'https://www.berlingske.dk/opinion',
            'https://www.berlingske.dk/aok',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse) #, meta={'dont_cache': True})
        # Possible login code.
       
       #login_url = 'https://www.berlingske.dk/mine-sider/kundeservice#login'

        #scrapy.FormRequest.from_response(
        #    response,
        #    formid='login_form'
        #    formdata={'email' : 'email', : 'password' : 'password'},
        #    clickdata={'class':'login-box__submit btn btn-primary order-sm-4 order-lg-3 submit'}
        #    callback=self.after_login,
        #)

    def parse(self, response):
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
