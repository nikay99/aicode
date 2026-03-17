.PHONY: install test clean run-example repl format lint help

help:
	@echo "AICode Development Commands"
	@echo "=========================="
	@echo "install      - Install package in development mode"
	@echo "test         - Run test suite"
	@echo "test-verbose - Run tests with verbose output"
	@echo "run-example  - Run example files"
	@echo "repl         - Start AICode REPL"
	@echo "clean        - Clean build artifacts"
	@echo "format       - Format code with black"
	@echo "lint         - Run flake8 linter"

install:
	pip install -e .

test:
	python3 -m pytest tests/test_aicode.py -v

test-verbose:
	python3 -m pytest tests/test_aicode.py -v --tb=short

run-example:
	@echo "Running examples..."
	@python3 main.py run examples/hello.aic
	@python3 main.py run examples/fizzbuzz.aic
	@python3 main.py run examples/demo.aic

repl:
	python3 main.py repl

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:
	black src/ tests/ main.py

lint:
	flake8 src/ tests/ --max-line-length=100
