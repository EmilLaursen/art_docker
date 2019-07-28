from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from artscraper.spiders.berlingske import BerlingskeScraper
from artscraper.spiders.dr import DrSpider
from artscraper.spiders.finans import FinansSpider
from artscraper.spiders.jposten import JpostenSpider



configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(DrSpider)
    yield runner.crawl(BerlingskeScraper)
    yield runner.crawl(FinansSpider)
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished