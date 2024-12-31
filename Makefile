.PHONY: install, run-demo, ruff, help

install:
	poetry install
	pre-commit install

run-demo:
	python3 examples/demo.py

ruff:
	ruff format
	ruff check

help:
	@echo "Available commands:"
	@echo "  install   - Install dependencies and set up pre-commit hooks"
	@echo "  ruff    - Format code and fix linting issues using ruff"
	@echo "  run-demo  - Run /examples/demo.py file"
