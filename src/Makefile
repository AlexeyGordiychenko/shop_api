all: run

run:
	docker compose --profile dev up -d

run-postgres:
	docker compose --profile dev up -d postgres-dev

build:
	docker compose --profile dev build

stop:
	docker compose --profile dev down

restart: stop run

clear:
	docker compose --profile dev down --volumes

test:
	docker compose run --rm -T app-test || true
	docker compose --profile test down

test-build:
	docker compose --profile test build

env-files:
	echo "DB_PORT=5433\nDB_PASSWORD=postgres" > .env
	echo "DB_PASSWORD=postgres" > .env_test

generate-migration:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

migrate:
	alembic upgrade head

rollback:
	alembic downgrade -1
