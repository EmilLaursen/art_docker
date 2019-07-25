import logging

from prometheus_client.twisted import MetricsResource
from prometheus_client import Counter, Summary, Gauge
from twisted.web.server import Site
from twisted.web import server, resource
from twisted.internet import task
from scrapy.exceptions import NotConfigured
from scrapy.utils.reactor import listen_tcp
from scrapy import signals
import re

logger = logging.getLogger(__name__)

prefix = 'spr_'

defaults = [
    'downloader/request_bytes',
    'downloader/request_count',
    'downloader/request_method_count/GET',
    'downloader/response_bytes',
    'downloader/response_count',
    'downloader/response_status_count/200',
    'dupefilter/filtered',
    'elapsed_time_seconds',
    'httpcache/firsthand',
    'httpcache/hit',
    'httpcache/miss',
    'httpcache/store',
    'item_dropped_count',
    'item_dropped_reasons_count/DropItem',
    'item_scraped_count',
    'log_count/INFO',
    'memusage/max',
    'memusage/startup',
    'offsite/domain',
    'offsite/filtered',
    'request_depth_max',
    'response_received_count',
    'robotstxt/request_count',
    'robotstxt/response_count',
    'robotstxt/response_status_count/200',
    'scheduler/dequeued',
    'scheduler/dequeued/memory',
    'scheduler/enqueued',
    'scheduler/enqueued/memory',
]
defaults = [re.sub(r'([^a-zA-Z0-9_:]+)', '_', d) for d in defaults]

class WebService(Site):
    """

    """
    def __init__(self, crawler):
        if not crawler.settings.getbool('PROMETHEUS_ENABLED', True):
            raise NotConfigured
        
        self.tasks = []
        self.stats = crawler.stats
        self.crawler = crawler
        self.name = crawler.settings.get('BOT_NAME')
        self.port = crawler.settings.get('PROMETHEUS_PORT', [9410])
        self.host = crawler.settings.get('PROMETHEUS_HOST', '0.0.0.0')
        self.path = crawler.settings.get('PROMETHEUS_PATH', 'metrics')
        self.interval = crawler.settings.get('PROMETHEUS_UPDATE_INTERVAL', 30)

        self.seen_stats = {}
        for default in defaults:
            g = Gauge(prefix + default, '', ['spider'])
            g.labels(spider=self.name).set(0)
            self.seen_stats[default] = g    
        
        # Global (non-spider level specific) stats     
        self.spr_opened = Gauge('spr_opened', 'Spider opened', ['spider'])
        self.spr_closed = Gauge(
            'spr_closed', 'Spider closed', ['spider', 'reason'])

        root = resource.Resource()
        self.promtheus = None
        root.putChild(self.path.encode('utf-8'), MetricsResource())
        server.Site.__init__(self, root)

        crawler.signals.connect(self.engine_started, signals.engine_started)
        crawler.signals.connect(self.engine_stopped, signals.engine_stopped)

        crawler.signals.connect(self.spider_opened, signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def engine_started(self):
        # Start server endpoint for exporting metrics
        self.promtheus = listen_tcp(self.port, self.host, self)

        # Periodically update the metrics
        tsk = task.LoopingCall(self.update)
        self.tasks.append(tsk)
        tsk.start(self.interval, now=True)

    def engine_stopped(self):
        # Stop all periodic tasks
        for tsk in self.tasks:
            if tsk.running:
                tsk.stop()

        # Stop metrics exporting
        self.promtheus.stopListening()

    def spider_opened(self, spider):
        self.spr_opened.labels(spider=self.name).inc()

    def spider_closed(self, spider, reason):
        self.spr_closed.labels(spider=self.name, reason=reason).inc()

    def update(self):
        logging.debug('prometheus.update stats: {}'.format(self.stats.get_stats()))

        for field, stat in self.stats.get_stats().items():
            if not isinstance(stat, int):
                continue
            
            try:
                field = re.sub(r'([^a-zA-Z0-9_:]+)', '_', field)
                if not re.match(r'([a-zA-Z_:][a-zA-Z0-9_:]*)', prefix + field):
                    raise ValueError('The gauge name {} does not conform to prometheus datamodel.'format(prefix + field))
                gauge = self.seen_stats.get(field)
                if not gauge:
                    gauge = Gauge(prefix + field, '', ['spider'])    
                gauge.labels(spider=self.name).set(stat)
                self.seen_stats[field] = gauge
            except ValueError as e:
                raise e