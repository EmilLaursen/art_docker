FROM python:3.7-alpine

COPY requirements.txt .

# you should document which build-deps are for which libs..

RUN apk add --no-cache make sqlite python3-dev gcc musl-dev openssl-dev libxml2-dev libxslt-dev libffi-dev libxml2 libxslt \
    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apk del make python3-dev gcc musl-dev openssl-dev libxml2-dev libxslt-dev libffi-dev

WORKDIR /artscraper

COPY . .

CMD ["uvicorn", "crawl_master_fastapi:app", "--host", "0.0.0.0", "--port", "5666"]