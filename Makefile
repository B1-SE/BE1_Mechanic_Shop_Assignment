.PHONY: help test tdd-red tdd-green tdd-refactor tdd-cycle install lint format security coverage

help:  ## Show this help message
	@echo "TDD & CI/CD Commands:"
	@echo "====================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:  ## Run all tests
	python -m pytest tests/ -v

test-watch:  ## Run tests in watch mode
	python -m pytest-watch tests/

tdd-red:  ## TDD RED phase - run failing tests
	python tdd_config.py --phase red

tdd-green:  ## TDD GREEN phase - run tests after implementation
	python tdd_config.py --phase green

tdd-refactor:  ## TDD REFACTOR phase - quality checks
	python tdd_config.py --phase refactor

tdd-cycle:  ## Run complete TDD cycle
	python tdd_config.py --phase cycle

tdd-watch:  ## TDD watch mode
	python tdd_config.py --watch

lint:  ## Run linting
	flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	black --check app/ tests/
	isort --check-only app/ tests/

format:  ## Format code
	black app/ tests/
	isort app/ tests/

security:  ## Run security checks
	bandit -r app/
	safety check

coverage:  ## Run tests with coverage
	python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

coverage-ci:  ## Run coverage for CI
	python -m pytest tests/ --cov=app --cov-report=xml --cov-fail-under=95

performance:  ## Run performance tests
	python -m pytest tests/ -k "performance" --durations=10

clean:  ## Clean up generated files
	rm -rf .coverage htmlcov/ .pytest_cache/ reports/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

docker-build:  ## Build Docker image
	docker build -t mechanic-shop:latest .

docker-run:  ## Run Docker container
	docker run -p 5000:5000 mechanic-shop:latest

ci-local:  ## Run CI pipeline locally
	make lint
	make security
	make coverage-ci
	make performance