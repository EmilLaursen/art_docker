from artscraper.spiders.generic_news_spider import NewssiteFrontpageSpider

startpage_links = [
    "https://www.dr.dk/nyheder/allenyheder/indland",
    "https://www.dr.dk/nyheder/allenyheder/udland",
    "https://www.dr.dk/nyheder/allenyheder/penge",
    "https://www.dr.dk/nyheder/allenyheder/politik",
    "https://www.dr.dk/nyheder/allenyheder/sporten",
    "https://www.dr.dk/nyheder/allenyheder/kultur",
    "https://www.dr.dk/nyheder/allenyheder/viden",
    "https://www.dr.dk/nyheder/allenyheder/mitliv",
    "https://www.dr.dk/nyheder/allenyheder/p4",
    "https://www.dr.dk/nyheder/allenyheder/vejret",
    "https://www.dr.dk/nyheder/allenyheder/",
]


default_selectors = {
    "startpage_follow_css": ".heading-small a::attr(href)",
    "article_follow_css": ".dre-teaser a::attr(href)",
    "paywall_css": ".paid",
    "authors_css": ".dre-article-byline__author span::text",
    "alt_authors_css": ".noAltAuthors",
    "date_css": ".dre-article-byline__date::text",
    "title_css": ".dre-article-title__title::text",
    "sub_title_css": ".dre-article-title__summary::text",
    "body_css": ".dre-article-body__paragraph",
    "section_css": ".dre-section-label__title--link::text",
    "startpage_links": startpage_links,
    "predicate_loader_pairs": [],
}


class DrFrontpage(NewssiteFrontpageSpider):
    name = "dr_frontpage"
    allowed_domains = ["dr.dk"]

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
        super(DrFrontpage, self).__init__(*args, **kwargs)
