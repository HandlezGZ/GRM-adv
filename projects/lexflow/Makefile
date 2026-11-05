VENV ?= $(shell if [ -d .venv ]; then echo .venv; elif [ -d ../../.venv ]; then echo ../../.venv; else echo ""; fi)
PYTHON ?= $(if $(VENV),$(VENV)/bin/python,python3)
PYTEST ?= $(if $(VENV),$(VENV)/bin/pytest,pytest)
RUFF ?= $(if $(VENV),$(VENV)/bin/ruff,ruff)
UVICORN ?= $(if $(VENV),$(VENV)/bin/uvicorn,uvicorn)
STREAMLIT ?= $(if $(VENV),$(VENV)/bin/streamlit,streamlit)

.PHONY: install test lint seed run-backend run-frontend docker-up docker-down

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt -r frontend/requirements.txt

test:
	PYTHONPATH=. $(PYTEST) backend/tests -v

lint:
	$(RUFF) check backend frontend scripts

seed:
	PYTHONPATH=. $(PYTHON) scripts/seed_demo_data.py

run-backend:
	PYTHONPATH=. $(UVICORN) backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	$(STREAMLIT) run frontend/app.py --server.port 8501

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
