build:
	docker build -t classyfireproxy .

server-compose-interactive:
	docker-compose build
	docker-compose --compatibility up

server-compose:
	docker-compose build
	docker-compose --compatibility up -d

server-compose-production:
	docker-compose build
	docker-compose -f docker-compose.yml -f docker-compose-production.yml --compatibility up -d

bash:
	docker run -it classyfireproxy /bin/bash 

attach:
	docker exec -it classyfireproxy /bin/bash 

query_populate:
	docker exec -it classyfireproxy /app/query_populate.py ${ID}

query_populate_json:
	docker exec -it classyfireproxy /app/query_populate_json.py ${JSON_DIR}

query_populate_json_dump:
	docker exec -it classyfireproxy /app/query_populate_json.py /data/dump

dump:
	docker exec -it classyfireproxy /app/dump_entities.py