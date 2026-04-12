@echo off
REM Quick Start Script for NASA EONET Data Cloud Project (Windows)
REM Usage: setup.bat

echo.
echo ======================================
echo 🌍 NASA EONET Data Cloud Setup
echo ======================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

echo ✓ Docker is installed

REM Create data directories
echo Creating data directories...
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
echo ✓ Data directories created

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    (
        echo ############################
        echo # POSTGRES DATA WAREHOUSE
        echo ############################
        echo PGHOST=localhost
        echo PGPORT=5433
        echo PGDATABASE=events_db
        echo PGUSER=airflow
        echo PGPASSWORD=airflow
        echo.
        echo ############################
        echo # NASA API
        echo ############################
        echo NASA_API_BASE_URL=https://eonet.gsfc.nasa.gov/api/v3/events
        echo NASA_API_KEY=demo
        echo COLLECTION_INTERVAL=3600
        echo.
        echo ############################
        echo # AIRFLOW
        echo ############################
        echo AIRFLOW_IMAGE_NAME=apache/airflow:2.7.3
        echo AIRFLOW__CORE__EXECUTOR=LocalExecutor
        echo AIRFLOW__CORE__LOAD_EXAMPLES=False
        echo AIRFLOW__CORE__FERNET_KEY=d60ynQfsD3wf4S1tdEsVQ8-OfysT0sQvW0UH7Tl9SKE=
        echo AIRFLOW_UID=50000
        echo AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres_dw/airflow
        echo.
        echo ############################
        echo # MINIO ^(Data Lake^)
        echo ############################
        echo MINIO_ROOT_USER=admin
        echo MINIO_ROOT_PASSWORD=password
        echo MINIO_ENDPOINT=minio:9000
        echo.
        echo ############################
        echo # MONITORING
        echo ############################
        echo PROMETHEUS_PORT=9090
        echo GRAFANA_PORT=3000
    ) > .env
    echo ✓ .env file created
) else (
    echo ✓ .env file already exists
)

echo.
echo Starting Docker services...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo ======================================
echo ✓ Setup Complete!
echo ======================================
echo.
echo Available services:
echo   • Airflow UI:        http://localhost:8080 ^(admin/admin^)
echo   • Dashboard:         http://localhost:8050
echo   • MinIO Console:     http://localhost:9001 ^(admin/password^)
echo   • Grafana:           http://localhost:3000 ^(admin/admin^)
echo   • Prometheus:        http://localhost:9090
echo   • PostgreSQL:        localhost:5433
echo.
echo Next steps:
echo   1. Install Python dependencies: pip install -r requirements.txt
echo   2. Setup database: python src/db_setup.py
echo   3. Test collector: python -m src.collectors.nasa_collector
echo   4. Run dashboard: python dashboards/app.py
echo.
echo View logs:
echo   docker-compose logs -f airflow-webserver
echo.

pause
