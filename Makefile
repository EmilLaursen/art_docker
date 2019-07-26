default: build

build:
	git pull
	docker build -t artscraper:latest $(HOME)/repos/art_docker/artscraper
	docker tag artscraper:latest emillime/artscraper:latest
	docker login
	docker push emillime/artscraper:latest
run:
	HOSTNAME=$(hostname) docker stack deploy -c $(HOME)/repos/prometheus/docker-stack.yml prom
full:
	make build
	make run