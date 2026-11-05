.PHONY: install test lint seed run-backend run-frontend docker-up docker-down

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r backend/requirements.txt -r frontend/requirements.txt

test:
	PYTHONPATH=. .venv/bin/pytest backend/tests -v

lint:
	.venv/bin/ruff check backend frontend scripts

seed:
	PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py

run-backend:
	PYTHONPATH=. .venv/bin/uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	.venv/bin/streamlit run frontend/app.py --server.port 8501

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
