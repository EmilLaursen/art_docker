#!/usr/bin/env python3
import subprocess

dr_spider = 'scrapy crawl drspider'

process = subprocess.Popen(dr_spider, shell=True)
print('Will this print before it is done?')

print(process)
print(process.poll())

