import scrapy
from artscraper.items import ArtscraperItem
from scrapy.loader import ItemLoader

class BerlingskeScraper(scrapy.Spider):
    name = 'arts'
    allowed_domains = ['berlingske.dk']
    

    def start_requests(self):

        urls = [
            'https://www.berlingske.dk/business'
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
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
