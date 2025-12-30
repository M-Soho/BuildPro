.PHONY: help install dev migrate upgrade test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make dev       - Run development server"
	@echo "  make migrate   - Create new migration"
	@echo "  make upgrade   - Run migrations"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linters"
	@echo "  make format    - Format code"
	@echo "  make clean     - Clean cache files"

install:
	pip install -r requirements-dev.txt

dev:
	./scripts/dev.sh

migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

test:
	pytest

lint:
	ruff check .
	black --check .
	mypy app

format:
	ruff check --fix .
	black .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
