build:
	docker build -t classyfireproxy .

server-compose-interactive:
	docker-compose build
	docker-compose up

server-compose:
	docker-compose build
	docker-compose up -d

bash:
	docker run -it classyfireproxy /bin/bash 

query_populate:
	docker exec -it classyfireproxy  /app/query_populate.py ${ID}
