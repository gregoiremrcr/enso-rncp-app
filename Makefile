.PHONY: up down test lint etl
up:
	docker compose up --build
down:
	docker compose down
test:
	cd backend && pytest
	cd etl && pytest
	cd frontend && npm test -- --run
lint:
	cd backend && ruff check . && black --check .
	cd etl && ruff check . && black --check .
	cd frontend && npm run lint && npm run format:check
etl:
	docker compose run --rm etl
