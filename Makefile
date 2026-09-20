# Saphira AI monorepo build targets
.PHONY: install install-dev lint typecheck security test agents-test ci clean

install:
	uv pip install -r requirements.txt
	pip install -e .

install-dev:
	uv pip install -r requirements-dev.txt
	pip install -e ".[dev]"

lint:
	ruff check packages agents src tests || true

typecheck:
	mypy packages agents || true

security:
	bandit -r packages agents src -ll || true
	pip-audit -r requirements.txt || true

test:
	pytest -q --tb=short

agents-test:
	pytest -q agents --tb=short

ci: lint typecheck security test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
