#!/usr/bin/env python3
import subprocess
import time
from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource
import psutil

dr_spider = "scrapy crawl drspider"
berlingske = "scrapy crawl arts"
bt_sitemap = "scrapy crawl bt_sitemap"
arbejderen = "scrapy crawl arbejderen"
kristeligt = "scrapy crawl kristeligt"
finans = "scrapy crawl finans"
dr_frontpage = "scrapy crawl dr_frontpage"
bt_frontpage = "scrapy crawl berlingske_frontpage"

minute = 60
hour = minute * 60

process = None
running = False

app = Flask(__name__)
api = Api(app)


def _crawler_running():
    global process
    has_run = process is not None
    running = has_run and process.poll() is None
    return running


def _start_crawler(crawler):
    global process
    if _crawler_running():
        return {"error": "Crawler " + str(process.args) + "is already running."}
    process = subprocess.Popen(crawler, shell=True)
    return {"success": "Crawler " + str(process.args) + " started."}


class BtFrontpage(Resource):
    def get(self):
        return _start_crawler(bt_frontpage)


class Dr(Resource):
    def get(self):
        return _start_crawler(dr_spider)


class BtSitemap(Resource):
    def get(self):
        return _start_crawler(bt_sitemap)


class Bt(Resource):
    def get(self):
        return _start_crawler(berlingske)


class Arb(Resource):
    def get(self):
        return _start_crawler(arbejderen)


class Krist(Resource):
    def get(self):
        return _start_crawler(kristeligt)


class Finans(Resource):
    def get(self):
        return _start_crawler(finans)


class DrFrontpage(Resource):
    def get(self):
        return _start_crawler(dr_frontpage)


class Stop(Resource):
    def get(self):
        global process
        if _crawler_running():
            args = str(process.args)
            process.send_signal(subprocess.signal.SIGINT)
            process.wait()
            process = None
            return {"success": "Crawler " + args + " stopped."}
        else:
            process = None
            return {"error": "No crawler running."}


class Processes(Resource):
    def get(self):
        res = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=["pid", "name", "username"])
            except psutil.NoSuchProcess:
                pass
            else:
                res.append(pinfo)
        return jsonify(res)


class Test(Resource):
    def get(self):
        ls = subprocess.Popen("ls", stdout=subprocess.PIPE, shell=True)
        pwd = subprocess.Popen("pwd", stdout=subprocess.PIPE, shell=True)

        ls = str(ls.stdout.read(30).decode("utf-8"))
        pwd = str(pwd.stdout.read(30).decode("utf-8"))

        du = subprocess.Popen("ping 192.168.0.10", stdout=subprocess.PIPE, shell=True)
        du1 = str(du.stdout.read(200).decode("utf-8"))
        du.send_signal(subprocess.signal.SIGINT)
        du2 = str(du.stdout.read(200).decode("utf-8"))

        return {"proc": process, "ls": ls, "pwd": pwd, "du": du1, "stop": du2}


api.add_resource(DrFrontpage, "/start/dr_frontpage", endpoint="dr_frontpage")
api.add_resource(Finans, "/start/finans", endpoint="finans")
api.add_resource(Krist, "/start/kristeligt", endpoint="kristeligt")
api.add_resource(Arb, "/start/arbejderen", endpoint="arbejderen")
api.add_resource(Dr, "/start/drspider", endpoint="drspider")
api.add_resource(BtSitemap, "/start/bt_sitemap", endpoint="bt_sitemap")
api.add_resource(BtFrontpage, "/start/bt_frontpage", endpoint="bt_frontpage")
api.add_resource(Bt, "/start/bt", endpoint="bt")
api.add_resource(Stop, "/stop", endpoint="stop")
api.add_resource(Test, "/test", endpoint="test")
api.add_resource(Processes, "/ps")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5666, debug=True)
