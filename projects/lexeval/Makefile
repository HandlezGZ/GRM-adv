VENV ?= /home/handlez/Work/GRM-adv-proj/GRM-adv/.venv
PYTHON ?= $(VENV)/bin/python3
PYTEST ?= $(VENV)/bin/pytest
RUFF ?= $(VENV)/bin/ruff
UVICORN ?= $(VENV)/bin/uvicorn
STREAMLIT ?= $(VENV)/bin/streamlit

.PHONY: help install seed test test-unit test-integration lint format run-backend run-frontend docker-up docker-down

help:
	@echo "LexEval — Continuous AI Evaluation & Quality Monitoring Platform"
	@echo "Available commands:"
	@echo "  make install        Install package and dependencies"
	@echo "  make seed           Seed golden tax dataset and baseline prompts"
	@echo "  make test           Run complete test suite (unit + integration)"
	@echo "  make lint           Check code quality with ruff"
	@echo "  make format         Auto-format code with ruff"
	@echo "  make run-backend    Start FastAPI backend server on port 8001"
	@echo "  make run-frontend   Start Streamlit dashboard on port 8502"
	@echo "  make docker-up      Start all services with Docker Compose"
	@echo "  make docker-down    Stop Docker Compose containers"

install:
	pip install -e .[dev]

seed:
	PYTHONPATH=. $(PYTHON) scripts/seed_golden_dataset.py

test:
	PYTHONPATH=. $(PYTEST) backend/tests -v

test-unit:
	PYTHONPATH=. $(PYTEST) backend/tests/unit -v

test-integration:
	PYTHONPATH=. $(PYTEST) backend/tests/integration -v

lint:
	$(RUFF) check .

format:
	$(RUFF) check --fix .

run-backend:
	PYTHONPATH=. $(UVICORN) backend.app.main:app --host 0.0.0.0 --port 8001 --reload

run-frontend:
	BACKEND_URL=http://127.0.0.1:8001 $(STREAMLIT) run frontend/app.py --server.port 8502 --server.address 0.0.0.0

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
