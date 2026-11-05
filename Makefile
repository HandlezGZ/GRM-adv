ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
VENV := $(shell if [ -d $(ROOT_DIR)/.venv ]; then echo $(ROOT_DIR)/.venv; else echo ""; fi)
PYTHON := $(if $(VENV),$(VENV)/bin/python,python3)
PYTEST := $(if $(VENV),$(VENV)/bin/pytest,pytest)
RUFF := $(if $(VENV),$(VENV)/bin/ruff,ruff)
UVICORN := $(if $(VENV),$(VENV)/bin/uvicorn,uvicorn)
STREAMLIT := $(if $(VENV),$(VENV)/bin/streamlit,streamlit)

.PHONY: install-all test-all lint-all test-lexflow seed-lexflow run-lexflow-backend run-lexflow-frontend docker-up docker-down

install-all:
	python3 -m venv $(ROOT_DIR)/.venv && . $(ROOT_DIR)/.venv/bin/activate && pip install -r $(ROOT_DIR)/projects/lexflow/backend/requirements.txt -r $(ROOT_DIR)/projects/lexflow/frontend/requirements.txt

test-all: test-lexflow
	@echo "All monorepo test suites executed successfully."

lint-all:
	$(RUFF) check $(ROOT_DIR)/projects/

test-lexflow:
	@echo "==> Running LexFlow test suite..."
	cd $(ROOT_DIR)/projects/lexflow && PYTHONPATH=. $(PYTEST) backend/tests -v

seed-lexflow:
	@echo "==> Seeding LexFlow demo requests..."
	cd $(ROOT_DIR)/projects/lexflow && PYTHONPATH=. $(PYTHON) scripts/seed_demo_data.py

run-lexflow-backend:
	cd $(ROOT_DIR)/projects/lexflow && PYTHONPATH=. $(UVICORN) backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-lexflow-frontend:
	cd $(ROOT_DIR)/projects/lexflow && $(STREAMLIT) run frontend/app.py --server.port 8501

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
