from fastapi import FastAPI
from enum import Enum
import subprocess
import psutil


app = FastAPI()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ScrapyProcess(metaclass=Singleton):
    def __init__(self):
        if not hasattr(self, "process"):
            self.process = None

    def launch(self, spider: str):
        if not self._crawler_running():
            self.process = subprocess.Popen(f"scrapy crawl {spider}", shell=True)
            return {"success": "Crawler " + str(self.process.args) + " started."}
        else:
            return {"failure": "Crawler " + str(self.process.args) + " is already running."}

    def stop(self):
        if self._crawler_running():
            args = str(self.process.args)
            self.process.send_signal(subprocess.signal.SIGINT)
            returncode = self.process.wait()
            self.process = None
            return {"success": f"Crawler {args} stopped. Returncode {returncode}"}
        return {"failure": "No crawler running."}

    def _crawler_running(self):
        hasrun = self.process is not None
        return hasrun and self.process.poll() is None


class Spider(str, Enum):
    bt_frontpage = "bt_frontpage"
    dr_frontpage = "dr_frontpage"
    finans_frontpage = "finans_frontpage"
    kristeligt_frontpage = "kristeligt_frontpage"
    arbejderen_frontpage = "arbejderen_frontpage"

@app.get("/start/{spider}")
async def launch_spider(spider: Spider):
    return ScrapyProcess().launch(spider)


@app.get("/stop")
async def stop():
    return ScrapyProcess().stop()


@app.get("/ps")
async def ps():
    res = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name", "username"])
            res.append(pinfo)
        except psutil.NoSuchProcess:
            pass

    return {"processes": res}


@app.get("/test")
async def test():

    ls = subprocess.Popen("ls", stdout=subprocess.PIPE, shell=True)
    pwd = subprocess.Popen("pwd", stdout=subprocess.PIPE, shell=True)

    ls = str(ls.stdout.read(30).decode("utf-8"))
    pwd = str(pwd.stdout.read(30).decode("utf-8"))

    du = subprocess.Popen("ping 192.168.0.10", stdout=subprocess.PIPE, shell=True)
    du1 = str(du.stdout.read(200).decode("utf-8"))
    du.send_signal(subprocess.signal.SIGINT)
    du2 = str(du.stdout.read(200).decode("utf-8"))

    return {"ls": ls, "pwd": pwd, "du": du1, "stop": du2}