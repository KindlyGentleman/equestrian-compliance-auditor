.PHONY: help install test test-demo lint format dev-backend dev-frontend build-frontend docker-build docker-up docker-down clean

PYTHON ?= python
PYTEST ?= pytest
UVICORN ?= uvicorn

help:
	@echo "Available commands:"
	@echo "  make install         Install backend dependencies and build tools"
	@echo "  make test            Run full backend test suite"
	@echo "  make test-demo       Run stakeholder demo verification (<90s benchmark)"
	@echo "  make lint            Run ruff linter checks"
	@echo "  make format          Run ruff code formatter"
	@echo "  make dev-backend     Start FastAPI backend server with hot-reload"
	@echo "  make dev-frontend    Start Next.js frontend dev server"
	@echo "  make build-frontend  Build Next.js production bundle"
	@echo "  make docker-build    Build Docker images for backend and frontend"
	@echo "  make docker-up       Run full stack via Docker Compose"
	@echo "  make docker-down     Stop Docker Compose containers"
	@echo "  make clean           Remove caches and temporary artifacts"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"
	cd frontend && npm install

test:
	$(PYTEST) backend/tests/ -v

test-demo:
	$(PYTEST) backend/tests/test_stakeholder_demo_e2e.py -v

lint:
	ruff check backend/

format:
	ruff format backend/

dev-backend:
	$(UVICORN) backend.app.main:app --host 127.0.0.1 --port 8000 --reload

dev-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/out 2>/dev/null || true
