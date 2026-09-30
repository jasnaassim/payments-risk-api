.PHONY: install data dbt run test lint

install:
	pip install -r requirements-dev.txt

data:
	python scripts/generate_transactions.py
	python scripts/load_local.py

dbt:
	cd dbt && dbt build --profiles-dir .

run:
	uvicorn app.main:app --reload

test:
	pytest -v

lint:
	ruff check .
