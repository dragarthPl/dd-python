.PHONY: check-all
check-all:
	poetry run black -l 120 .
	poetry run isort .
	poetry run ruff check .
	poetry run mypy .

.PHONY: check-mypy
check-mypy:
	poetry run mypy .

.PHONY: test
test:
	poetry run pytest .
