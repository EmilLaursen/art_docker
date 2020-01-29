# TODO

- [] Upload scraped data to S3 directly.
- [] crawl_master needs alot of work.
- [] Refactor all spiders to common base class.
- [] Bring all scraped data to common format, and resave to S3.
- [] Recalculate bloom filters (messed up the berlingske filter.)
- [] Document VisitedFilter middleware.
- [] Document Prometheus exporter middleware.
- [] Figure out how to operate on full list of fields, and each scraped field (Scrapy Itemloader docs). Use this to apply TakeFirst, and removedupes where appropriate.
- [] Use w3lib to remove tags. Compare speed with html2text.
- [] Use scrapyd to orchestrate spiders. Need to eggify spiders.



# Custom middleware

- persisting dupefilter using a bloomfilter.
- prometheus exporter.