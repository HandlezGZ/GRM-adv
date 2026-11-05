.PHONY: help test lint format seed run-backend run-frontend clean

PYTHON ?= python3
PYTEST ?= pytest
RUFF ?= ruff
UVICORN ?= uvicorn
STREAMLIT ?= streamlit

help:
	@echo "LexTax - Tax Document Analysis Assistant Makefile"
	@echo "Targets:"
	@echo "  test         - Run test suite with pytest"
	@echo "  lint         - Lint code using ruff"
	@echo "  format       - Fix and format code with ruff"
	@echo "  seed         - Populate database with synthetic tax documents"
	@echo "  run-backend  - Start FastAPI backend on port 8002"
	@echo "  run-frontend - Start Streamlit frontend on port 8503"
	@echo "  clean        - Remove temporary caches and sqlite databases"

test:
	PYTHONPATH=. $(PYTEST) backend/tests -v

lint:
	$(RUFF) check backend frontend scripts

format:
	$(RUFF) check backend frontend scripts --fix

seed:
	$(PYTHON) scripts/seed_tax_data.py

run-backend:
	$(UVICORN) backend.app.main:app --host 0.0.0.0 --port 8002 --reload

run-frontend:
	$(STREAMLIT) run frontend/app.py --server.port 8503 --server.address 0.0.0.0

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ backend/**/__pycache__ frontend/**/__pycache__
