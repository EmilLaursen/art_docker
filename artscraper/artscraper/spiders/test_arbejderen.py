from artscraper.spiders.generic_news_spider import NewssiteFrontpageSpider
from urllib.parse import urlsplit, unquote

startpage_links = [
    "http://www.arbejderen.dk/",
    "https://arbejderen.dk/blogs",
    "https://arbejderen.dk/arbejde-og-kapital",
    "https://arbejderen.dk/idekamp",
    "https://arbejderen.dk/kultur",
    "https://arbejderen.dk/indland",
    "https://arbejderen.dk/udland",
    "https://arbejderen.dk/marx",
    "https://arbejderen.dk/teori",
    "https://arbejderen.dk/s-regering",
    "https://arbejderen.dk/ok20",
    "https://arbejderen.dk/ghettolov",
    "https://arbejderen.dk/livsstil",
    "https://arbejderen.dk/v%C3%A5benindustri",
    "https://arbejderen.dk/social-dumping",
    "https://arbejderen.dk/tags/eu-modstand",
    "https://arbejderen.dk/krig",
    "https://arbejderen.dk/kalender",
    "https://arbejderen.dk/navne",
]


def is_blog_url(url):
    return (
        _get_section(url) == "blog-indlæg"
        or _get_section(url) == "blog-indl%C3%A6g"
        or "/blogs" in url
    )


def _get_section(url):
    splitpath = urlsplit(url).path.split(sep="/")
    section = splitpath[1] if len(splitpath) >= 1 else None
    return unquote(section)


def section_loader(itemloader, response):
    itemloader.add_value("section", _get_section(response.url))
    return itemloader


def debatindlaeg_loader(itemloader, response):
    itemloader.add_value("paywall", False)
    itemloader.add_css(
        "authors",
        ".views-row-first.views-row-last .views-field-name .field-content::text",
    )
    itemloader.add_css("title", "h1::text")
    itemloader.add_css("date", ".pane-node-created .pane-content::text")
    itemloader.add_css("sub_title", ".manchet::text")
    itemloader.add_css("body", ".pane-node-body p")
    return itemloader


default_selectors = {
    "startpage_follow_css": "h1 a::attr(href)",
    "article_follow_css": ".views-row div a::attr(href)",
    "paywall_css": ".pane-block-10",
    "alt_authors_css": "#page-aside-beta .views-row-last span::text",
    "authors_css": ".skribenttitel::text",
    "date_css": ".created::text",
    "title_css": ".pane-page-title h1::text",
    "sub_title_css": ".manchet, .manchetOld::text",
    "body_css": ".even p",
    "section_css": "",
    "startpage_links": startpage_links,
    "predicate_loader_pairs": [
        (is_blog_url, debatindlaeg_loader),
        (lambda x: True, section_loader),
    ],
}


class ArbejderenFrontpage(NewssiteFrontpageSpider):
    name = "arbejderen_frontpage"
    allowed_domains = ["arbejderen.dk"]
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
        super(ArbejderenFrontpage, self).__init__(*args, **kwargs)

    def choose_follow_css(self, response):
        if is_blog_url(response.url):
            return ".field-content a::attr(href)"
        elif response.url in self.startpage_links:
            return self.startpage_follow_css
        return self.article_follow_css

