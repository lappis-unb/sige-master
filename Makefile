up:
	if docker network ls | grep -q smi-network
	then
		echo "network exists";
	else
		docker network create smi-network;
	fi

	docker-compose up -d

stop:
	docker-compose stop

down:
	docker-compose down

dump:
	docker-compose up -d
	docker-compose exec master-api python manage.py dumpdata > dump-db.json

loaddump:
	docker-compose up -d
	docker-compose exec master-api python manage.py loaddata dump-db.json

fixhstore:
	docker-compose exec master-db psql -U postgres -c 'create extension hstore;'

