# Scrapy news site scraper (ARM edition)

This is a small Scrapy app, for scraping new articles off of the front pages of news sites.

# Container stack

The app is deployed with docker swarm. This stack is based on the wonderful work of [vegasbrianc/prometheus](https://github.com/vegasbrianc/prometheus) and consists of Prometheus, Node Exporter, Grafana, cAdvisor, and Alertmanager for monitoring the containers. Note that the cAdvisor image used, is for ARM. If you wish to deploy this on a non-arm architecture, you should change this image to Google's official cAdvisor image.


The repo contains some custom Prometheus exporters.
1) A Scrapy Prometheus exporter (artscraper/prometheus.py), which publishes the internal spider stats to Prometheus. It is a slight modification of [this](https://github.com/rangertaha/scrapy-prometheus-exporter). It will publish all internal Scrapy stats in the Spider.stats.get_stats() dictionary, including stats added by your own custom middleware.
2) Using Node exporters Text Collector plugin, we publish the total file size of the scraped data (given you save the data on the host), along with the CPU temperature.
   1) This is done with the scripts ```export_scraped_file_size.py``` and ```temp.sh```. To achieve atomic writes, I have the following line in my host crontab. Here PATH is the full path to the art_docker repo.
   
``` * * * * * python3 PATH/export_scraped_file_size.py -e jsonl -d PATH/data/ -o PATH/.metrics/file_sizes.prom.$$ && mv PATH/.metrics/file_sizes.prom.$$ /node_exporter/textfile_collector/file_sizes.prom```



# How to use it

Nothing fancy. Just consult makefile. Just build the scraper image with appropriate tags, then deploy the docker-stack.yml.

A rudimentary web API has been written to orchestrate the different spiders. It should block you from running more than one spider at a time.
Swagger documentation is available at
```IP-TO-HOST:5666/docs```
To launch a scraper you can hit ```curl -XGET IP-TO-HOST:5666/start/SCRAPER_NAME ```.

# Extending the NewssiteFrontpageSpider class
Depending on the site, it should be easy to extend the generic spider class, to support novel news sites.

You need to figure out CSS-selectors for the relevant fields and get a bunch of start page links, to act as entry points for scraping. Sometimes this is all there is to it.

On some sites, different sections require custom logic. For example, the blog/discussion section needs specific CSS-selectors for some fields, and for URLs to new articles. For custom fields, use the predicate_loader_pairs to supply pairs
```(pred, loader)```
where ```(pred(response)```( is a predicate which decides if custom logic is needed based on the response, and the loader(itemloader, response) overwrites CSS-selector logic on the itemloader. See the current spider for example.



# TODO

- [*] Upload scraped data to S3 directly.
- [] Use AWS Lambda to zip the scraped .jsonl files every week.
- [*] crawl_master needs a lot of work.
- [*] Refactor all spiders to a common base class.
- [] Bring all scraped data to a common format, and resave to S3.
- [*] Recalculate bloom filters (messed up the Berlingske filter.)
- [] Document VisitedFilter middleware.
- [] Document Prometheus exporter middleware.
- [*] Figure out how to operate on a full list of fields, and each scraped field (Scrapy Itemloader docs). Use this to apply TakeFirst, and remove dupes where appropriate.
- [*] Use w3lib to remove tags. Compare speed with html2text.
- [] Use Scrapyd to orchestrate spiders. Need to eggify spiders.
- [] Data duplicate detection. Several Ritzau articles on all sites.
- [] Use AWS Lambda to calculate daily stats about scraped data. Either make a weekly report or push to influx DB or Prometheus for Grafana integration.



# Custom middleware

- persisting request dupe filter using a bloom filter.
- Prometheus exporter.