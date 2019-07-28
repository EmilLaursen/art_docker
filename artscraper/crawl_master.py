#!/usr/bin/env python3
import subprocess
import time

dr_spider = ['scrapy', 'crawl', 'drspider']
berlingske = ['scrapy', 'crawl', 'arts']

process = subprocess.run(berlingske)

if process.returncode == 0:
    print('finished now?')

time.sleep(30)

process = subprocess.run(dr_spider)


time.sleep(30)


process = subprocess.run(berlingske)