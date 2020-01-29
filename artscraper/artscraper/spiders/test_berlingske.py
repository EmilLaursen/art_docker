from artscraper.spiders.generic_news_spider import NewssiteFrontpageSpider

startpage_links = [
    "https://www.berlingske.dk/",
    "https://www.berlingske.dk/business",
    "https://www.berlingske.dk/nyheder",
    "https://www.berlingske.dk/opinion",
    "https://www.berlingske.dk/aok",
    "https://www.berlingske.dk/kommentarer",
    "https://www.berlingske.dk/oekonomi",
    "https://www.berlingske.dk/virksomheder",
    "https://www.berlingske.dk/karriere",
    "https://www.berlingske.dk/privatoekonomi",
    "https://www.berlingske.dk/business",
    "https://www.berlingske.dk/aktier",
    "https://www.berlingske.dk/usa/",
]


default_selectors = {
    "startpage_follow_css": ".dre-item a::attr(href), .teaser__title-link::attr(href)",
    "article_follow_css": ".dre-item a::attr(href), .teaser__title-link::attr(href)",
    "paywall_css": ".paid",
    "alt_authors_css": ".font-g1::text",
    "authors_css": ".article-byline__author-name::text",
    "date_css": ".article-byline__date::text",
    "title_css": ".article-header__title::text",
    "sub_title_css": ".article-header__intro::text",
    "body_css": "#articleBody h2 , #articleBody p",
    "section_css": "#articleHeader .d-inline-block::text",
    "startpage_links": startpage_links,
    "predicate_loader_pairs": [],
}


class BtFrontpage(NewssiteFrontpageSpider):
    name = "bt_frontpage"
    allowed_domains = ["berlingske.dk"]

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
        super(BtFrontpage, self).__init__(*args, **kwargs)
