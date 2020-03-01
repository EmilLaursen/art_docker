default: build

build:
	echo 'Clean dangling images, volumes and containers'
	#docker stack rm prom
	#docker images -qf dangling=true | xargs -r docker image rm
	#docker volume ls -qf dangling=true | xargs -r docker volume rm
	#docker ps --filter status=dead --filter status=exited -aq | xargs -r docker rm -v
	# Or docker system prune --force. But this seems to mess with running containers.
	docker build -f $$(pwd)/artscraper/Dockerfile -t emillime/artscraper:latest $$(pwd)/artscraper
run:
	docker stack rm prom
	echo "Sleeping for 30s"
	sleep 30
	echo "Waking up!"
	HOSTNAME=$$(hostname) docker stack deploy -c docker-stack.yml prom
pull:
	git pull
push:
	docker login
	docker push emillime/artscraper:latest
full:
	make build
	make run