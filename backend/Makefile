.PHONY: install dev start clean format lint check docker-build docker-up docker-down docker-logs

install:
	uv venv
	uv pip install -r requirements.txt

format:
	black .
	isort .

lint:
	ruff check . --fix
	mypy .

check: format lint

dev:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

start:
	uv run uvicorn main:app --host 0.0.0.0 --port 8000

celery:
	uv run celery -A task.celery_app worker --loglevel=info

celery-beat:
	uv run celery -A task.celery_app beat --loglevel=info

flower:
	uv run celery -A task.celery_app flower --port=5555

docker-build:
	docker compose -f docker-compose.yml build

docker-up:
	docker compose -f docker-compose.yml up

docker-down:
	docker compose -f docker-compose.yml down --rmi all --volumes --remove-orphans

docker-logs:
	docker compose -f docker-compose.yml logs -f

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 