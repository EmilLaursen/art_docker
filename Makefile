default: build

build:
	docker build -t artscraper:v.0.4 $(HOME)/repos/art_docker/artscraper
run:
	HOSTNAME=$(hostname) docker stack deploy -c $(HOME)/repos/prometheus/docker-stack.yml prom