#!/bin/bash
# Quick Start Script for NASA EONET Data Cloud Project
# Usage: bash setup.sh

set -e  # Exit on error

echo "======================================"
echo "🌍 NASA EONET Data Cloud Setup"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "✗ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "✗ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker Compose is installed"

# Create data directories
echo "Creating data directories..."
mkdir -p data/raw
mkdir -p data/processed
echo "✓ Data directories created"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
############################
# POSTGRES DATA WAREHOUSE
############################
PGHOST=localhost
PGPORT=5433                    
PGDATABASE=events_db
PGUSER=airflow
PGPASSWORD=airflow

############################
# NASA API
############################
NASA_API_BASE_URL=https://eonet.gsfc.nasa.gov/api/v3/events
NASA_API_KEY=demo
COLLECTION_INTERVAL=3600

############################
# AIRFLOW
############################
AIRFLOW_IMAGE_NAME=apache/airflow:2.7.3
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__FERNET_KEY=d60ynQfsD3wf4S1tdEsVQ8-OfysT0sQvW0UH7Tl9SKE=
AIRFLOW_UID=50000

AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres_dw/airflow

############################
# MINIO (Data Lake)
############################
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=password
MINIO_ENDPOINT=minio:9000

############################
# MONITORING
############################
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Start Docker services
echo ""
echo "Starting Docker services..."
docker-compose up -d

echo ""
echo "Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "healthy"; then
    echo "✓ Services are running"
else
    echo "⚠️  Some services may still be initializing..."
fi

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Available services:"
echo "  • Airflow UI:        http://localhost:8080 (admin/admin)"
echo "  • Dashboard:         http://localhost:8050"
echo "  • MinIO Console:     http://localhost:9001 (admin/password)"
echo "  • Grafana:           http://localhost:3000 (admin/admin)"
echo "  • Prometheus:        http://localhost:9090"
echo "  • PostgreSQL:        localhost:5433"
echo ""
echo "Next steps:"
echo "  1. Install Python dependencies: pip install -r requirements.txt"
echo "  2. Setup database: python src/db_setup.py"
echo "  3. Test collector: python -m src.collectors.nasa_collector"
echo "  4. Run dashboard: python dashboards/app.py"
echo ""
echo "View logs:"
echo "  docker-compose logs -f airflow-webserver"
echo ""
