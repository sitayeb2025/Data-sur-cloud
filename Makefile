# Makefile for NASA EONET Data Cloud Project
# Usage: make [target]

.PHONY: help setup start stop logs clean test install

help:
	@echo "🌍 NASA EONET Data Cloud - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup & Infrastructure:"
	@echo "  make install        - Install Python dependencies"
	@echo "  make setup          - Setup infrastructure (Docker + DB)"
	@echo "  make start          - Start Docker services"
	@echo "  make stop           - Stop Docker services"
	@echo "  make restart        - Restart all services"
	@echo "  make clean          - Stop and remove all containers"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests"
	@echo "  make verify         - Verify setup"
	@echo "  make logs           - View Docker logs"
	@echo ""
	@echo "Data Operations:"
	@echo "  make collect        - Run collector manually"
	@echo "  make transform      - Run transformer manually"
	@echo "  make analyze        - Run analysis"
	@echo "  make dashboard      - Start dashboard"
	@echo ""
	@echo "Database:"
	@echo "  make db-setup       - Setup PostgreSQL tables"
	@echo "  make db-query       - Query database"
	@echo ""
	@echo "Services:"
	@echo "  make airflow        - Open Airflow UI (http://localhost:8080)"
	@echo "  make dashboard-url  - Open Dashboard (http://localhost:8050)"
	@echo "  make minio          - Open MinIO (http://localhost:9001)"
	@echo ""

install:
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

setup: start db-setup
	@echo "✓ Setup complete!"

start:
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Waiting for services to initialize..."
	sleep 10

stop:
	docker-compose stop
	@echo "✓ Services stopped"

restart:
	docker-compose restart
	@echo "✓ Services restarted"

clean:
	docker-compose down
	-rm -rf data/raw/*
	-rm -rf data/processed/*
	-rm -rf minio_data/
	-rm -rf postgres_data/
	-rm -rf grafana_data/
	@echo "✓ Cleanup complete"

logs:
	docker-compose logs -f airflow-webserver

test:
	python -m pytest tests/ -v

verify:
	python verify_setup.py

collect:
	python -m src.collectors.nasa_collector

transform:
	python -m src.etl.transformer

analyze:
	python -m src.analysis.analysis

dashboard:
	python dashboards/app.py

db-setup:
	python src/db_setup.py

db-query:
	docker-compose exec postgres psql -U airflow -d events_db

airflow:
	@echo "Opening Airflow UI at http://localhost:8080"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8080 || \
	command -v open >/dev/null 2>&1 && open http://localhost:8080 || \
	echo "Please open http://localhost:8080 in your browser"

dashboard-url:
	@echo "Opening Dashboard at http://localhost:8050"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8050 || \
	command -v open >/dev/null 2>&1 && open http://localhost:8050 || \
	echo "Please open http://localhost:8050 in your browser"

minio:
	@echo "Opening MinIO at http://localhost:9001"
	@command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:9001 || \
	command -v open >/dev/null 2>&1 && open http://localhost:9001 || \
	echo "Please open http://localhost:9001 in your browser"
