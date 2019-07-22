FROM python:3.7-alpine

RUN apk add --no-cache python-dev gcc musl-dev openssl-dev libxml2-dev libxslt-dev libffi-dev libxml2 libxslt \
    && pip3 install scrapy \
    && apk del python-dev gcc musl-dev openssl-dev libxml2-dev libxslt-dev libffi-dev

WORKDIR /artscraper

COPY . .

VOLUME /data

CMD scrapy crawl arts -o data/arts.jl