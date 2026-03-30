.PHONY: up down test test-backend test-frontend logs migrate lint

# === Local Development ===

up:
	docker compose up -d
	@echo "Backend: http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	@echo "Frontend: run 'cd frontend && npm run dev' separately"

down:
	docker compose down

logs:
	docker compose logs -f

# === Database ===

migrate:
	cd backend && alembic upgrade head

migration:
	cd backend && alembic revision --autogenerate -m "$(msg)"

# === Testing ===

test: test-backend test-frontend

test-backend:
	cd backend && pip install -e ".[dev]" -q && pytest tests/ -v

test-frontend:
	cd frontend && npm test -- --run

# === Linting ===

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint
