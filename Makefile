.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help up down build test lint format worker beat shell seed styleguide migrate makemigrations logs sync

help: ## Lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

up: ## Sobe todo o stack de dev (web, worker, beat, redis, postgres, minio)
	$(COMPOSE) up --build

down: ## Derruba o stack
	$(COMPOSE) down

build: ## (Re)constrói as imagens
	$(COMPOSE) build

test: ## Roda a suíte de testes (pytest) no container web
	$(COMPOSE) run --rm -e RUN_MIGRATIONS=0 web pytest --ds=justavalia.core.settings.test

lint: ## Lint + checagem de formatação (ruff) — local via uv
	uv run ruff check .
	uv run ruff format --check .

format: ## Formata e corrige com ruff — local via uv
	uv run ruff format .
	uv run ruff check --fix .

worker: ## Sobe apenas o worker Celery
	$(COMPOSE) up worker

beat: ## Sobe apenas o Celery beat
	$(COMPOSE) up beat

shell: ## Abre o shell do Django
	$(COMPOSE) run --rm web python manage.py shell

seed: ## Popula dados de exemplo (stub na Fase 0)
	$(COMPOSE) run --rm -e RUN_MIGRATIONS=0 web python manage.py seed

styleguide: ## Renderiza o styleguide interno (stub na Fase 0)
	$(COMPOSE) run --rm -e RUN_MIGRATIONS=0 web python manage.py styleguide

migrate: ## Aplica migrações
	$(COMPOSE) run --rm web python manage.py migrate

makemigrations: ## Gera migrações
	$(COMPOSE) run --rm -e RUN_MIGRATIONS=0 web python manage.py makemigrations

logs: ## Segue os logs do stack
	$(COMPOSE) logs -f

sync: ## Instala/atualiza dependências locais (uv)
	uv sync
