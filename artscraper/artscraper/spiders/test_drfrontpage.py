from artscraper.spiders.generic_news_spider import NewssiteFrontpageSpider

startpage_links = [
    "https://www.dr.dk/nyheder/indland",
    "https://www.dr.dk/nyheder/udland",
    "https://www.dr.dk/nyheder/penge",
    "https://www.dr.dk/nyheder/politik",
    "https://www.dr.dk/nyheder/regionale",
    "https://www.dr.dk/sporten",
    "https://www.dr.dk/nyheder/kultur",
    "https://www.dr.dk/nyheder/vejret",
    "https://www.dr.dk/nyheder/viden",
    "https://www.dr.dk/nyheder",
]


default_selectors = {
    "startpage_follow_css": ".heading-small::attr(href) , .heading-xsmall::attr(href) , h3::attr(href) , .heading-xxlarge::attr(href) , .dre-teaser-title--md-large::attr(href) , .dre-teaser-title--md-x-small::attr(href) , .dre-teaser-title--lg-small::attr(href) , .dre-teaser-title--xxs-x-small::attr(href) , .dre-teaser-title--xs-x-small::attr(href)",
    "article_follow_css": ".dre-teaser a::attr(href)",
    "paywall_css": ".paid",
    "authors_css": ".dre-article-byline__author span::text",
    "alt_authors_css": ".noAltAuthors",
    "date_css": ".dre-article-byline__date::text",
    "title_css": ".dre-article-title__title::text",
    "sub_title_css": ".dre-article-title__summary::text",
    "body_css": ".dre-article-body p, .dre-article-body__fact-box-content p, .dre-article-body-paragraph",
    "section_css": ".dre-label-text--sm-large::text",
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
