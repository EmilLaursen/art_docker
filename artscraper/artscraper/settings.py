# -*- coding: utf-8 -*-

# Scrapy settings for artscraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from pathlib import Path

BOT_NAME = "artscraper"

SPIDER_MODULES = ["artscraper.spiders"]
NEWSPIDER_MODULE = "artscraper.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'artscraper (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'artscraper.middlewares.ArtscraperSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {"artscraper.middlewares.VisitedFilter": 121}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    #    'scrapy.extensions.telnet.TelnetConsole': None,
    "artscraper.prometheus.WebService": 500
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "artscraper.pipelines.ContentHash": 500,
    "artscraper.pipelines.ScrapeStatsPersistancePipeline": 800,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'data/httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = [] # status codes to ignore. Default.
# HTTPCACHE_GZIP = True
# HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.RFC2616Policy'
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

DEPTH_STATS_VERBOSE = True

# MISSING STATS DB FILE
MISSING_STATS_DB_FILE = "data/missing_stats.db"
# LOGGING
LOG_FILE = "data/logs/overwrite_name.log"  # this nameing trick does not work here! Overwrite in spider
LOG_LEVEL = "INFO"
LOG_FORMATTER = (
    "artscraper.pipelines.PoliteLogFormatter"  # Custom DropItem log handling.
)

# Visited BloomFilter
VISITED_FILTER_MAX_ELEMENTS = 4000000
VISITED_FILTER_ERROR_RATE = 1e-9
VISITED_FILTER_PATH = (
    "data/%(name)s.filter"  # this nameing trick does not work here! Overwrite in spider
)
# Urls which will never be cached.
NEVER_CACHE = []

# Use BFS order.
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = "scrapy.squeues.PickleFifoDiskQueue"
SCHEDULER_MEMORY_QUEUE = "scrapy.squeues.FifoMemoryQueue"
SCHEDULER_DEBUG = True

# PROMETHEUS Module settings
PROMETHEUS_ENABLED = True
PROMETHEUS_PORT = [6080]
PROMETHEUS_HOST = "0.0.0.0"
PROMETHEUS_PATH = "metrics"
PROMETHEUS_UPDATE_INTERVAL = 20

# FEED EXPORTER
#FEED_URI = Path.cwd().as_uri() + "/data/%(name)s.jsonl"
FEED_FORMAT = "jsonlines"
FEED_URI = "s3://dk-new-scrape/%(name)s/%(time)s.jsonl"

minute = 60
hour = minute * 60

# STOPPING CONDITION
CLOSESPIDER_TIMEOUT = hour * 5
CLOSESPIDER_ITEMCOUNT = 11111
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ERRORCOUNT = 0
