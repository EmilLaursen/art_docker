from urllib.parse import urlsplit, unquote
from artscraper.spiders.generic_news_spider import NewssiteFrontpageSpider


def _get_section(url):
    splitpath = urlsplit(url).path.split(sep="/")
    section = splitpath[1] if len(splitpath) >= 1 else None
    return unquote(section)


def is_debatindlaeg_url(response):
    return (
        _get_section(response.url) == "debatindlaeg"
    )  # or self._get_section(url) == 'blog-indl%C3%A6g'


def debatindlaeg_loader(itemloader, response):
    body = response.css("#new_recommendation+ .article p::text").getall()
    author = body[0] if body else body
    itemloader.add_value("authors", author)
    return itemloader


startpage_links = [
    "https://www.kristeligt-dagblad.dk/",
    "https://www.kristeligt-dagblad.dk/bagsiden/",
    "https://www.kristeligt-dagblad.dk/udland/",
    "https://www.kristeligt-dagblad.dk/danmark/",
    "https://www.kristeligt-dagblad.dk/liv-sjael/",
    "https://www.kristeligt-dagblad.dk/kronik/",
    "https://www.kristeligt-dagblad.dk/kirke",
    "https://www.kristeligt-dagblad.dk/kultur",
    "https://www.kristeligt-dagblad.dk/liv",
    "https://www.kristeligt-dagblad.dk/debat",
    "https://www.kristeligt-dagblad.dk/om",
    "https://www.kristeligt-dagblad.dk/genforeningen",
]


default_selectors = {
    "startpage_follow_css": ".heading+ .column a::attr(href) , .related a::attr(href) , .heading a::attr(href)",
    "article_follow_css": ".link::attr(href)",
    "paywall_css": ".paid",
    "authors_css": ".byline a::text",
    "date_css": ".publication::text",
    "title_css": "#new_recommendation+ .article h1::text",
    "sub_title_css": ".lead::text",
    "body_css": "#new_recommendation+ .article p",
    "section_css": ".artSec::text",
    "startpage_links": startpage_links,
    "predicate_loader_pairs": [(is_debatindlaeg_url, debatindlaeg_loader)],
}


class KristeligtFrontpage(NewssiteFrontpageSpider):

    name = "kristeligt_frontpage"

    allowed_domains = ["kristeligt-dagblad.dk"]

    custom_settings = {
        "BOT_NAME": name,
        "LOG_FILE": f"data/logs/{name}.log",
        "VISITED_FILTER_PATH": f"data/{name}.filter",
        "NEVER_CACHE": startpage_links,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, *args, **kwargs):
        # Inject configuration.
        kwargs["newssite"] = default_selectors
        super(KristeligtFrontpage, self).__init__(*args, **kwargs)