.PHONY: install dev start clean format lint check

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

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 