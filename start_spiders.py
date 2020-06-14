#!/usr/bin/env python3
import requests
import plac


spiders = "finans_frontpage arbejderen_frontpage dr_frontpage kristeligt_frontpage bt_frontpage".split()
endpoint = "http://0.0.0.0:5666/start/"


def main(spider: (f"The spider to run. Must be one of {spiders}", "option", "run")):
    if not spider in spiders:
        print("Must supply valid spider name")

    requests.get(endpoint + spider)


if __name__ == "__main__":
    plac.call(main)

