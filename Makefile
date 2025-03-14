.PHONY: test

default:
    $(eval env ?= dev)

env ?= dev stage prod
ifeq (,$(filter $(env),dev stage prod))
	$(error Error: env variable must be dev, stage or prod)
endif

$(info [$(env) environment])

ifeq ($(env),prod)
	export VERSION := $(shell git describe --tags --abbrev=0)
else
	export VERSION := $(shell git rev-parse --short HEAD)
endif

ifeq ($(env),dev)
	FILE_ARGS=-f docker-compose.dev.yml
else
	FILE_ARGS=-f docker-compose.prod.yml
endif

log_lines := 10

up: build-api
	@echo "Up App"
	docker compose $(FILE_ARGS) up -d

down:
	@echo "Down App"
	docker compose $(FILE_ARGS) down

build-api:
	@echo "Build App"
	docker build -t fastapi-tdd/api:$(VERSION) .

logs-%:
	@echo "App logs"
	docker compose $(FILE_ARGS) logs -t -f --tail $(log_lines) $(*)

api-attach:
	@echo "App attach"
	@echo "Use ^p and ^q to quit"
	docker attach $(docker ps --filter name="-api-" -q)

test:
	tox

# ===== Optional ===== #

up-postgres:
	@echo "Start PostgreSQL"
	@docker compose $(FILE_ARGS) up -d postgres

up-redis:
	@echo "Start Redis"
	@docker compose $(FILE_ARGS) up -d redis
