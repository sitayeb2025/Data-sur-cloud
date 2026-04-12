# 🌍 NASA EONET Global Disasters Analytics

**Plateforme complète d'analyse des catastrophes naturelles mondiales en temps réel**

Collecte, transformation et visualisation des données NASA Earth Observatory Network avec 10,000+ événements mondiaux

## 🎯 Résumé

✅ **10,000+ événements** naturels (incendies, tremblements de terre, tempêtes)  
✅ **3 dashboards interactifs** (17 graphiques au total)  
✅ **Geo-localisés** sur 10 régions mondiales  
✅ **94.44% qualité** de données  

## 🚀 Démarrage rapide

\\\ash
# Installation
pip install -r requirements.txt

# Lancez les dashboards (3 terminaux)
python dashboards/compact_app.py        # Port 8053 - Rapport rapide
python dashboards/advanced_app.py       # Port 8051 - Exploration avancée
python dashboards/ultra_advanced_app.py # Port 8052 - Analyse scientifique
\\\

## 📊 Dashboards

| Dashboard | Port | Graphiques | Cible |
|-----------|------|-----------|--------|
| Compact | 8053 | 5 essentiels | Décideurs |
| Advanced | 8051 | 8 + Filtres | Analystes |
| Ultra | 8052 | 9 scientifiques | Data Scientists |

**Graphiques inclus:** Carte mondiale, Heatmaps, Timelines, 3D Scatter, Violin Plot, Polar Radar, Correlation Matrix, Sankey, Funnel, et plus...

## 📁 Structure

\\\
src/              Collecteurs (NASA, USGS) + ETL + Analysis
data/             Données brutes (JSON) + Traitées (Parquet)
dashboards/       4 applications Dash interactives
docker-compose.yml Infrastructure complète
\\\

## 🔧 Technologies

Python 3.11 • Dash • Plotly • Pandas • Docker • PostgreSQL • MinIO

## 📈 Données

- **Total:** 10,000+ événements
- **Régions:** 10 (Amérique du Nord, Afrique, Asie, etc.)
- **Types:** 6 (Incendies, Tremblements de terre, Tempêtes, Inondations, Volcans, Glace)
- **Période:** Juillet 2024 - Avril 2026

## 📄 Licence

MIT License - Open Source

---

🌍 *Plateforme de monitoring des catastrophes naturelles mondiales*
