.PHONY: run

default: run

define set-default-container
	ifndef c
	c = server
	else ifeq (${c},all)
	override c=
	endif
endef

define use-env
	include .env
#	export
endef


set-container:
	$(eval $(call set-default-container))

build: set-container
	docker-compose build ${c}

build-no-cache: set-container
	docker-compose build --no-cache ${c}
run:
	docker-compose up -d --force-recreate ${c}

dev:
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d --force-recreate ${c}

restart: set-container
	docker-compose restart ${c}

stop: set-container
	docker-compose stop ${c}

down:
	docker-compose down

exec: set-container
	docker-compose exec ${c} /bin/bash

log: set-container
	docker-compose logs -f ${c}

makemigrations:
	docker-compose exec server ./manage.py makemigrations

migrate: makemigrations
	docker-compose exec server ./manage.py migrate

