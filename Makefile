ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
VENV := $(shell if [ -d $(ROOT_DIR)/.venv ]; then echo $(ROOT_DIR)/.venv; else echo ""; fi)
PYTHON := $(if $(VENV),$(VENV)/bin/python,python3)
PYTEST := $(if $(VENV),$(VENV)/bin/pytest,pytest)
RUFF := $(if $(VENV),$(VENV)/bin/ruff,ruff)
UVICORN := $(if $(VENV),$(VENV)/bin/uvicorn,uvicorn)
NODE_BIN := $(shell if [ -d $(ROOT_DIR)/../.node/bin ]; then echo $(ROOT_DIR)/../.node/bin; elif [ -d $(HOME)/.local/share/mise/installs/node/latest/bin ]; then echo $(HOME)/.local/share/mise/installs/node/latest/bin; else echo ""; fi)

.PHONY: install-all test-all lint-all seed-all build-frontends \
	test-lexflow seed-lexflow run-lexflow-backend run-lexflow-frontend \
	test-lexeval seed-lexeval run-lexeval-backend run-lexeval-frontend \
	test-tax-assistant seed-tax run-tax-backend run-tax-frontend \
	docker-up docker-down

install-all:
	$(PYTHON) -m pip install -r $(ROOT_DIR)/projects/lexflow/backend/requirements.txt \
		-r $(ROOT_DIR)/projects/tax-assistant/requirements.txt \
		-r $(ROOT_DIR)/projects/lexeval/pyproject.toml
	cd $(ROOT_DIR)/projects/lexflow/frontend && PATH="$(NODE_BIN):$$PATH" npm install
	cd $(ROOT_DIR)/projects/lexeval/frontend && PATH="$(NODE_BIN):$$PATH" npm install
	cd $(ROOT_DIR)/projects/tax-assistant/frontend && PATH="$(NODE_BIN):$$PATH" npm install

test-all: test-lexflow test-lexeval test-tax-assistant build-frontends
	@echo "=========================================================="
	@echo "All 3 backend test suites and all 3 React frontend builds"
	@echo "executed successfully with zero errors!"
	@echo "=========================================================="

build-frontends:
	@echo "==> Building React frontends..."
	cd $(ROOT_DIR)/projects/lexflow/frontend && PATH="$(NODE_BIN):$$PATH" ./node_modules/.bin/vite build
	cd $(ROOT_DIR)/projects/lexeval/frontend && PATH="$(NODE_BIN):$$PATH" ./node_modules/.bin/vite build
	cd $(ROOT_DIR)/projects/tax-assistant/frontend && PATH="$(NODE_BIN):$$PATH" ./node_modules/.bin/vite build

lint-all:
	@echo "==> Running Ruff check across all backend projects..."
	$(RUFF) check $(ROOT_DIR)/projects/

seed-all: seed-lexflow seed-lexeval seed-tax
	@echo "==> All demonstration data seeded across monorepo."

# -------------------------------------------------------------
# Project 1: LexFlow (Process Automation & Request Triage)
# -------------------------------------------------------------
test-lexflow:
	@echo "==> [LexFlow] Running backend test suite..."
	cd $(ROOT_DIR)/projects/lexflow && PYTHONPATH=. $(PYTEST) backend/tests -v

seed-lexflow:
	@echo "==> [LexFlow] Seeding demo requests..."
	cd $(ROOT_DIR)/projects/lexflow && PYTHONPATH=. $(PYTHON) scripts/seed_demo_data.py

run-lexflow-backend:
	cd $(ROOT_DIR)/projects/lexflow && PYTHONPATH=. $(UVICORN) backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-lexflow-frontend:
	cd $(ROOT_DIR)/projects/lexflow/frontend && PATH="$(NODE_BIN):$$PATH" ./node_modules/.bin/vite --port 8501 --host

# -------------------------------------------------------------
# Project 2: LexEval (AI Quality & Hallucination Monitoring)
# -------------------------------------------------------------
test-lexeval:
	@echo "==> [LexEval] Running backend test suite..."
	cd $(ROOT_DIR)/projects/lexeval && PYTHONPATH=. $(PYTEST) backend/tests -v

seed-lexeval:
	@echo "==> [LexEval] Seeding golden test dataset..."
	cd $(ROOT_DIR)/projects/lexeval && PYTHONPATH=. $(PYTHON) scripts/seed_golden_dataset.py

run-lexeval-backend:
	cd $(ROOT_DIR)/projects/lexeval && PYTHONPATH=. $(UVICORN) backend.app.main:app --reload --host 0.0.0.0 --port 8001

run-lexeval-frontend:
	cd $(ROOT_DIR)/projects/lexeval/frontend && PATH="$(NODE_BIN):$$PATH" ./node_modules/.bin/vite --port 8502 --host

# -------------------------------------------------------------
# Project 3: LexTax (Tax Document Analysis & Grounded Q&A)
# -------------------------------------------------------------
test-tax-assistant:
	@echo "==> [LexTax] Running backend test suite..."
	cd $(ROOT_DIR)/projects/tax-assistant && PYTHONPATH=. $(PYTEST) backend/tests -v

seed-tax:
	@echo "==> [LexTax] Seeding synthetic tax documents..."
	cd $(ROOT_DIR)/projects/tax-assistant && PYTHONPATH=. $(PYTHON) scripts/seed_tax_data.py

run-tax-backend:
	cd $(ROOT_DIR)/projects/tax-assistant && PYTHONPATH=. $(UVICORN) backend.app.main:app --reload --host 0.0.0.0 --port 8002

run-tax-frontend:
	cd $(ROOT_DIR)/projects/tax-assistant/frontend && PATH="$(NODE_BIN):$$PATH" ./node_modules/.bin/vite --port 8503 --host

# -------------------------------------------------------------
# Docker Orchestration
# -------------------------------------------------------------
docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
