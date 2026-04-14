.PHONY: bootstrap-csv install install-dev run-api run-dashboard run-worker docker-up docker-down test lint format migrate seed doctor

bootstrap-csv:
	@echo "🧪 Bootstrapping CSV Analysis Feature..."
	./venv/bin/pip install -r requirements.txt
	./venv/bin/python scripts/create_sample_csv.py
	make run

install:
	python3.11 -m venv venv
	./venv/bin/pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run-api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	streamlit run src/dashboard/app.py

run-worker:
	celery -A src.tasks.celery_app worker -B --loglevel=info

run: docker-up

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

test:
	./venv/bin/pytest tests/ -v

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

migrate:
	alembic upgrade head

seed:
	python scripts/seed_data.py

doctor:
	@echo "🔍 Checking System Health..."
	@docker --version || echo "❌ Docker not found"
	@docker compose version || echo "❌ Docker Compose not found"
	@curl -s http://localhost:8000/health || echo "❌ API not reachable at http://localhost:8000"
	@curl -s http://localhost:8501 || echo "❌ Dashboard not reachable at http://localhost:8501"
	@echo "✅ Check complete."
