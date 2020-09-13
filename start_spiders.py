#!/usr/bin/env python3
import requests
import argparse




spiders = "finans_frontpage arbejderen_frontpage dr_frontpage kristeligt_frontpage bt_frontpage".split()
endpoint = "http://0.0.0.0:5666/start/"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("spider", help=f"The spider to run. Must be one of {spiders}", type=str)
    args = parser.parse_args()


    if not args.spider in spiders:
        print("Must supply valid spider name")
        exit(1)

    requests.get(endpoint + args.spider)
