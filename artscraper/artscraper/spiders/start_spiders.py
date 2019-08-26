#!/usr/bin/env python3
import requests
import plac


spiders = "finans arbejderen dr_frontpage kristeligt bt_sitemap".split()
endpoint = "http://192.168.0.10:5666/start/"
def main(spider: (f"The spider to run. Must be one of {spiders}", "option", "run")):
    if not spider in spiders:
        print('Must supply valid spider name')
    
    requests.get(endpoint + spider)


if __name__ == '__main__':
    plac.call(main)