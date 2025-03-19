all: test

test:
	@echo "Running tests..."
	uv run pytest -v -s --cov ./unfazed_sentry --cov-report term-missing

format:
	@echo "Formatting code..."
	uv run ruff format tests/ unfazed_sentry/
	uv run ruff check tests/ unfazed_sentry/  --fix
	uv run mypy --check-untyped-defs --explicit-package-bases --ignore-missing-imports tests/ unfazed_sentry/

publish:
	@echo "Publishing package..."
	uv build
	uv publish
