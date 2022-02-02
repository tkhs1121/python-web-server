py:
	docker-compose exec python3 python app.py
build:
	docker-compose build --no-cache --force-rm
up:
	docker-compose up -d
down:
	docker-compose down
restart:
	@make down
	@make up