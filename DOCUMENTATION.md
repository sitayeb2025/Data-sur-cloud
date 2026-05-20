# Documentation du Projet Data Cloud

## 1. Collecte de Données

### API NASA EONET
**Endpoint:** `https://eonet.gsfc.nasa.gov/api/v3/events`

L'API fournit des événements naturels en temps réel:
- Tremblements de terre
- Volcans
- Tempêtes
- Inondations
- Incendies de forêt
- Et autres...

**Utilisation:**
```python
from src.collectors.nasa_collector import NASAEONETCollector

collector = NASAEONETCollector()
result = collector.collect(limit=100)
```

## 2. Pipeline ETL

### Étapes de transformation:

**1. Nettoyage (Clean)**
- Suppression des doublons
- Gestion des valeurs manquantes
- Validation des données

**2. Normalisation (Normalize)**
- Conversion des types de données
- Standardisation des formats
- Validation géographique

**3. Enrichissement (Enrich)**
- Calcul de scores de sévérité
- Classification par région
- Extraction de métriques

**4. Validation de Qualité**
- Vérification de l'intégrité
- Génération de rapports

## 3. Infrastructure

### Services Docker
- **PostgreSQL**: Data Warehouse
- **MinIO**: Data Lake (S3 local)
- **Airflow**: Orchestration ETL
- **Prometheus**: Métriques
- **Grafana**: Dashboards monitoring

### Démarrage:
```bash
docker-compose up -d
```

## 4. Base de Données

### Schema Principal

**Table: events**
- id (PK)
- title, description
- event_type, status
- latitude, longitude, region
- start_date, last_update
- severity_score, severity_category
- geometry_count, duration_days

**Vues:**
- `events_active`: Événements ouverts
- `events_high_severity`: Sévérité > 0.7
- `events_by_type`: Agrégation par type
- `events_by_region`: Agrégation par région

### Setup Initial:
```bash
cd src
python db_setup.py
```

## 5. DAG Airflow

**Pipeline:** `nasa_eonet_etl_pipeline`

Tâches:
1. `collect_events` - Collecte API
2. `transform_events` - Transformation ETL
3. `load_events` - Chargement PostgreSQL

Schedule: Quotidien à minuit

Accès: http://localhost:8080

## 6. Dashboard

Visualisations interactives avec Plotly/Dash:
- 🗺️ Carte géographique
- 📊 Distribution par type
- ⏱️ Timeline de sévérité
- ⚠️ Classification de sévérité

Accès: http://localhost:8050

## 7. Analyse des Données

```python
from src.analysis.analysis import EventsAnalyzer

analyzer = EventsAnalyzer("data/processed/events_processed_*.parquet")
report = analyzer.generate_report()
```

Génère:
- Rapport JSON
- Visualisations PNG
- Détection d'anomalies

## 8. Monitoring

**Prometheus:** http://localhost:9090
**Grafana:** http://localhost:3000

Métriques suivies:
- Nombre d'événements
- Latence de traitement
- Taux de succès du pipeline
- Utilisation des ressources

## 9. Git & GitHub  

```bash
git clone https://github.com/sitayeb2025/Data-sur-cloud.git
cd Data-sur-cloud

# Configuration initiale
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"

# Premier commit
git add .
git commit -m "Initial commit: Setup infrastructure NASA EONET"
git push origin main
```

## 10. Sécurité

✅ Secrets en variables d'environnement (.env)
✅ Pas de credentials en dur
✅ Logs avec audit trail
✅ Monitoring actif

## 11. Fichiers Importants

```
src/
├── collectors/nasa_collector.py  # Collecteur API
├── etl/transformer.py            # Pipeline ETL
├── analysis/analysis.py          # Analyses statistiques
└── db_setup.py                   # Configuration BDD

airflow/dags/
└── nasa_etl_dag.py               # DAG Airflow

dashboards/
└── app.py                        # App Dash

notebooks/
└── exploration.ipynb             # Notebook Jupyter
```

## 12. Commandes Utiles

```bash
# Installation dépendances
pip install -r requirements.txt

# Test collecteur
python -m src.collectors.nasa_collector

# Test transformer
python -m src.etl.transformer

# Test analyse
python -m src.analysis.analysis

# Setup BDD
python src/db_setup.py

# Lancer dashboard
python dashboards/app.py

# Logs Docker
docker-compose logs -f airflow-webserver
docker-compose logs -f airflow-scheduler

# Entrer dans conteneur
docker-compose exec postgres psql -U airflow

# Arrêter services
docker-compose down
```

## 13. Troubleshooting

### Erreur de connexion PostgreSQL
```bash
docker-compose restart postgres
# Attendre 30 secondes puis retry
```

### MinIO données corrompues
```bash
docker-compose down
rm -rf minio_data/
docker-compose up -d
```

### Airflow DAG not appearing
```bash
docker-compose restart airflow-scheduler
docker-compose logs -f airflow-scheduler
```

### Port déjà utilisé
```bash
# Changer le port dans docker-compose.yml
# Exemple: "8081:8080" au lieu de "8080:8080"
```

---

**Dernière mise à jour:** April 2024
