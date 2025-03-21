.PHONY: install dev start clean format lint check docker-build docker-up docker-down docker-logs docker-prune

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
	docker-compose -f docker-compose.yml build

docker-up:
	docker-compose -f docker-compose.yml up --build -d

docker-down:
	docker-compose -f docker-compose.yml down

# 사용법: make docker-logs [service]
# service: api, celery_worker, celery_beat, flower 등 (생략 시 모든 서비스)
docker-logs:
ifdef service
	docker-compose -f docker-compose.yml logs -f $(service)
else
	docker-compose -f docker-compose.yml logs -f
endif

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 

docker-prune:
	docker builder prune -f
