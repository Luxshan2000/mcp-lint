.PHONY: install dev test test-quick lint format check build clean publish publish-test

install:
	pip install .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-quick:
	pytest tests/ -x -q

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

check: format-check lint test

build: clean
	python -m build

clean:
	rm -rf dist/ build/ src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

publish: build
	twine upload dist/*

publish-test: build
	twine upload --repository testpypi dist/*
