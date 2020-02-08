from artscraper.spiders.generic_news_spider import NewssiteFrontpageSpider


startpage_links = [
    "http://www.finans.dk/",
    "https://finans.dk/analyse/",
    "https://finans.dk/indsigt/",
    "https://finans.dk/investor",
    "https://finans.dk/debat/",
    "https://finans.dk/erhverv/",
    "https://finans.dk/okonomi/",
    "https://finans.dk/finans2/",
    "https://finans.dk/tech/",
    "https://finans.dk/privatokonomi/",
]


default_selectors = {
    "startpage_follow_css": ".artRelLink::attr(href) , .baronContainer a::attr(href) , .artHd::attr(href), .card__title a::attr(href)",
    "article_follow_css": ".artHd a::attr(href) , .artRelatedColumnCnt a::attr(href)",
    "paywall_css": ".artViewLock__plate::text",
    "authors_css": ".popupCaller::text",
    "alt_authors_css": ".bylineArt p::text",
    "date_css": ".artTime::text",
    "title_css": "h1::text",
    "sub_title_css": ".artManchet::text",
    "body_css": ".artBody p",
    "section_css": ".artSec::text",
    "startpage_links": startpage_links,
    "predicate_loader_pairs": [],
}


class FinansFrontpage(NewssiteFrontpageSpider):
    name = "finans_frontpage"

    allowed_domains = ["finans.dk"]

    custom_settings = {
        "BOT_NAME": name,
        "LOG_FILE": f"data/logs/{name}.log",
        # 'JOBDIR' : 'data/' + name,
        "VISITED_FILTER_PATH": f"data/{name}.filter",
        "NEVER_CACHE": startpage_links,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, *args, **kwargs):
        # Inject configuration.
        kwargs["newssite"] = default_selectors
        super(FinansFrontpage, self).__init__(*args, **kwargs)
