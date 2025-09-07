.PHONY: help install test lint format clean

help:
	@echo "Available commands:"
	@echo "  install    Install the plugin in development mode"
	@echo "  test       Run the test suite"
	@echo "  lint       Run code linting"
	@echo "  format     Format code with black and isort"
	@echo "  clean      Clean build artifacts"

install:
	pip install -e .
	
test:
	python -m pytest enrollment_summary/tests/ -v --cov=enrollment_summary

lint:
	flake8 enrollment_summary/
	black --check enrollment_summary/
	isort --check-only enrollment_summary/

format:
	black enrollment_summary/
	isort enrollment_summary/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete