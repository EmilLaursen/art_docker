default: build

build:
	echo 'Clean dangling images, volumes and containers'
	#docker stack rm prom
	#docker images -qf dangling=true | xargs -r docker image rm
	#docker volume ls -qf dangling=true | xargs -r docker volume rm
	#docker ps --filter status=dead --filter status=exited -aq | xargs -r docker rm -v
	# Or docker system prune --force. But this seems to mess with running containers.
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