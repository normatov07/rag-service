include .env

build:
	docker compose down
	docker compose up -d --build
up:
	docker compose up -d
down:
	docker compose down
stop:
	docker compose stop

migrate:
	docker compose exec app sh -c 'python manage.py migrate'

makemigrations:
	docker compose exec app sh -c 'python manage.py makemigrations'

seed:


pgsql:
	docker compose exec pgsql bash -c 'psql -U ${DB_USER} -d ${DB_NAME}'

shell:
	docker compose exec app bash

grpc:
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. grpcdata.proto

translate_make:
	docker compose exec app sh -c 'python manage.py makemessages -l ru -l uz_Crl -l uz_Lat'
	
translate_compile:
	docker compose exec app sh -c 'python manage.py compilemessages'