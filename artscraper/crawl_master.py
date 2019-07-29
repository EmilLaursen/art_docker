#!/usr/bin/env python3
import subprocess
import time

dr_spider = ['scrapy', 'crawl', 'drspider']
berlingske = ['scrapy', 'crawl', 'arts']
bt_sitemap = ['scrapy', 'crawl', 'bt_sitemap']


minute = 60
hour = minute * 60


process = subprocess.run(bt_sitemap)