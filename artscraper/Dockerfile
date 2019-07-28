FROM python:3.7-alpine

COPY requirements.txt .

RUN apk add --no-cache python-dev gcc musl-dev openssl-dev libxml2-dev libxslt-dev libffi-dev libxml2 libxslt \
    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apk del python-dev gcc musl-dev openssl-dev libxml2-dev libxslt-dev libffi-dev

WORKDIR /artscraper

COPY . .

VOLUME /data

EXPOSE 6080

CMD scrapy crawl drspider