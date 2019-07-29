#!/usr/bin/env python3
import subprocess
import time

dr_spider = ['scrapy', 'crawl', 'drspider']
berlingske = ['scrapy', 'crawl', 'arts']


minute = 60
hour = minute * 60


process = subprocess.run(berlingske)

if process.returncode == 0:
    print('finished now?')

time.sleep(5*minute)

process = subprocess.run(dr_spider)