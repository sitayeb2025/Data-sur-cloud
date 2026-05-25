# 🚨 Civil Protection Monitoring System

> Surveillance des catastrophes naturelles mondiales — Pipeline ETL Cloud + Dashboard temps réel pour la Protection Civile.

![Python](https://img.shields.io/badge/Python-3.10+-blue) 
![Airflow](https://img.shields.io/badge/Airflow-2.7.3-red)
 ![Dash](https://img.shields.io/badge/Dash-2.14-green) 
 ![AWS](https://img.shields.io/badge/AWS-EC2%20Stockholm-yellow) 
 ![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## 🎯 But
Collecter automatiquement les données de catastrophes naturelles (NASA EONET + USGS), les transformer via un pipeline ETL orchestré par Airflow, et les visualiser dans un dashboard interactif pour aider la Protection Civile à prioriser ses interventions en temps réel.

## 🏗️ Architecture
```
NASA EONET + USGS API  →  Airflow DAG (@daily)  →  MinIO Data Lake  →  PostgreSQL  →  Dashboard Dash
```
| Couche | Tech |
|--------|------|
| Orchestration | Apache Airflow 2.7.3 |
| Dashboard | Dash 2.14 + Plotly 5.18 |
| Data Lake | MinIO (S3-compatible) |
| Base de données | PostgreSQL 13 |
| Monitoring | Prometheus + Grafana |
| Cloud | AWS EC2 — eu-north-1 Stockholm |
| Conteneurs | Docker Compose (7 containers) |

## 🚀 Lancement
```bash
git clone https://github.com/sitayeb2025/Data-sur-cloud.git && cd Data-sur-cloud
python -m venv venv           # Création de l’environnement virtuel Python
docker-compose up -d          # démarrer tous les services
pip install -r requirements.txt
python diagnostic_minio_collecte.py
python clean_and_analyze_data.py   # pipeline complet
python dashboards/app.py           # dashboard → http://localhost:8050
```

## 🔗 Accès aux services
| Service | URL | Login |
|---------|-----|-------|
| Dashboard | http://localhost:8050 | — |
| Airflow | http://localhost:8080 | admin / admin |
| MinIO | http://localhost:9001 | admin / password |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |

> Sur AWS EC2 remplacer `localhost` par l'IP publique. Ports Security Group à ouvrir : `8050` `8080` `9000` `9001` `3000` `9090`

## 👤 Auteur
**RYMA SITAYEB** — [github.com/sitayeb2025/Data-sur-cloud](https://github.com/sitayeb2025/Data-sur-cloud) — MIT