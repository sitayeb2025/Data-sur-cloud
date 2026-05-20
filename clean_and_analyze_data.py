"""
Nettoyage et analyse complète des données NASA
Récupère depuis MinIO, nettoie, analyse et sauvegarde
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*60)
print("🧹 NETTOYAGE ET ANALYSE DES DONNÉES")
print("="*60 + "\n")

# ÉTAPE 1: Charger depuis MinIO
print("1️⃣ Chargement des données depuis MinIO...")
print("-" * 60)

try:
    from src.storage.minio_client import MinIOClient
    
    client = MinIOClient()
    
    # Lister les fichiers parsés
    files = client.list_objects('raw-data', prefix='nasa_events/parsed/')
    json_files = [f for f in files if f.endswith('.json')]
    
    if not json_files:
        print("❌ Aucun fichier JSON trouvé dans MinIO")
        sys.exit(1)
    
    # Prendre le plus récent
    latest_file = sorted(json_files)[-1]
    print(f"📁 Fichier trouvé: {latest_file}")
    
    # Charger les données
    data = client.get_json('raw-data', latest_file)
    events = data.get('events') if isinstance(data, dict) else data
    
    if not events:
        print("❌ Aucun événement trouvé")
        sys.exit(1)
    
    print(f"✓ {len(events)} événements chargés")
    
except Exception as e:
    print(f"❌ Erreur chargement: {e}")
    sys.exit(1)

# ÉTAPE 2: Convertir en DataFrame
print("\n2️⃣ Conversion en DataFrame...")
print("-" * 60)

try:
    df = pd.DataFrame(events)
    print(f"✓ DataFrame créé: {df.shape[0]} lignes x {df.shape[1]} colonnes")
    print(f"  Colonnes: {', '.join(df.columns.tolist())}")
    
except Exception as e:
    print(f"❌ Erreur conversion: {e}")
    sys.exit(1)

# ÉTAPE 3: Nettoyage des données
print("\n3️⃣ Nettoyage des données...")
print("-" * 60)

try:
    initial_rows = len(df)
    
    # Supprimer les doublons
    df_clean = df.drop_duplicates(subset=['id'], keep='first')
    dupes_removed = initial_rows - len(df_clean)
    print(f"✓ Doublons supprimés: {dupes_removed}")
    
    # Supprimer les lignes avec coordonnées invalides
    df_clean = df_clean[
        (df_clean['latitude'].notna()) & 
        (df_clean['longitude'].notna()) &
        (df_clean['latitude'] != 0) &
        (df_clean['longitude'] != 0)
    ]
    coords_removed = len(df) - len(df_clean) - dupes_removed
    print(f"✓ Coordonnées invalides supprimées: {coords_removed}")
    
    # Supprimer les lignes avec événements manquants
    df_clean = df_clean[df_clean['event_type'].notna()]
    missing_removed = len(df) - len(df_clean) - dupes_removed - coords_removed
    print(f"✓ Événements manquants supprimés: {missing_removed}")
    
    # Remplir les valeurs manquantes
    df_clean['description'] = df_clean['description'].fillna('N/A')
    df_clean['status'] = df_clean['status'].fillna('unknown')
    
    print(f"\n✓ Nettoyage terminé: {len(df_clean)} lignes restantes")
    
except Exception as e:
    print(f"❌ Erreur nettoyage: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ÉTAPE 4: Analyse descriptive
print("\n4️⃣ Analyse descriptive...")
print("-" * 60)

try:
    # Statistiques de base
    print(f"\n📊 Statistiques de base:")
    print(f"  - Total événements: {len(df_clean)}")
    print(f"  - Période: {df_clean['collection_date'].min()} à {df_clean['collection_date'].max()}")
    
    # Types d'événements
    print(f"\n📈 Distribution par type d'événement:")
    event_counts = df_clean['event_type'].value_counts()
    for event_type, count in event_counts.items():
        pct = (count / len(df_clean)) * 100
        print(f"  - {event_type}: {count} ({pct:.1f}%)")
    
    # Statuts
    print(f"\n🔄 Distribution par statut:")
    status_counts = df_clean['status'].value_counts()
    for status, count in status_counts.items():
        pct = (count / len(df_clean)) * 100
        print(f"  - {status}: {count} ({pct:.1f}%)")
    
    # Géographie
    print(f"\n🌍 Géographie:")
    print(f"  - Latitude min: {df_clean['latitude'].min():.2f}°")
    print(f"  - Latitude max: {df_clean['latitude'].max():.2f}°")
    print(f"  - Longitude min: {df_clean['longitude'].min():.2f}°")
    print(f"  - Longitude max: {df_clean['longitude'].max():.2f}°")
    
    # Qualité des données
    null_counts = df_clean.isnull().sum()
    if null_counts.sum() > 0:
        print(f"\n⚠️ Valeurs manquantes:")
        for col, count in null_counts[null_counts > 0].items():
            print(f"   - {col}: {count}")
    else:
        print(f"\n✓ Pas de valeurs manquantes!")
    
except Exception as e:
    print(f"⚠️ Erreur analyse: {e}")

# ÉTAPE 5: Enrichissement des données
print("\n5️⃣ Enrichissement des données...")
print("-" * 60)

try:
    # Ajouter des colonnes d'enrichissement
    df_enriched = df_clean.copy()
    
    # Catégoriser la sévérité (basée sur le type)
    severity_map = {
        'wildfire': 'high',
        'cyclone': 'critical',
        'earthquake': 'high',
        'volcano': 'critical',
        'flood': 'medium',
        'storm': 'medium',
        'landslide': 'medium',
        'snow_ice': 'low',
        'bloom': 'low',
    }
    
    df_enriched['severity'] = df_enriched['event_type'].map(severity_map).fillna('unknown')
    
    # Ajouter région approximative
    def get_region(lat, lon):
        if lat > 50:
            return 'North America/Europe'
        elif lat > 20:
            return 'Middle Latitude'
        elif lat > -20:
            return 'Tropical'
        elif lat > -50:
            return 'South America/Africa'
        else:
            return 'Antarctica'
    
    df_enriched['region'] = df_enriched.apply(
        lambda row: get_region(row['latitude'], row['longitude']), 
        axis=1
    )
    
    # Timestamp de traitement
    df_enriched['processed_date'] = datetime.now().isoformat()
    
    print(f"✓ Enrichissement complété")
    print(f"  - Colonne 'severity' ajoutée")
    print(f"  - Colonne 'region' ajoutée")
    print(f"  - Colonne 'processed_date' ajoutée")
    
except Exception as e:
    print(f"⚠️ Erreur enrichissement: {e}")
    df_enriched = df_clean

# ÉTAPE 6: Sauvegarder les données nettoyées
print("\n6️⃣ Sauvegarde des données nettoyées...")
print("-" * 60)

try:
    # Sauvegarder en CSV localement
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    csv_file = f"data/processed/events_cleaned_{timestamp}.csv"
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df_enriched.to_csv(csv_file, index=False)
    print(f"✓ CSV local: {csv_file}")
    
    # Sauvegarder en Parquet localement
    parquet_file = f"data/processed/events_enriched_{timestamp}.parquet"
    df_enriched.to_parquet(parquet_file, index=False)
    print(f"✓ Parquet local: {parquet_file}")
    
    # Sauvegarder dans MinIO
    # CSV
    client.upload_file(
        'processed-data',
        f'cleaned/events_{timestamp}.csv',
        csv_file,
        content_type='text/csv'
    )
    print(f"✓ MinIO CSV: processed-data/cleaned/events_{timestamp}.csv")
    
    # Parquet
    client.upload_file(
        'processed-data',
        f'enriched/events_{timestamp}.parquet',
        parquet_file,
        content_type='application/octet-stream'
    )
    print(f"✓ MinIO Parquet: processed-data/enriched/events_{timestamp}.parquet")
    
except Exception as e:
    print(f"❌ Erreur sauvegarde: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ÉTAPE 7: Rapport final
print("\n7️⃣ Rapport d'analyse...")
print("-" * 60)

report = {
    'timestamp': datetime.now().isoformat(),
    'initial_events': initial_rows,
    'cleaned_events': len(df_clean),
    'enriched_events': len(df_enriched),
    'events_removed': initial_rows - len(df_clean),
    'event_types': event_counts.to_dict(),
    'statuses': status_counts.to_dict(),
    'regions': df_enriched['region'].value_counts().to_dict(),
    'severities': df_enriched['severity'].value_counts().to_dict(),
    'quality_score': ((len(df_enriched) / initial_rows) * 100) if initial_rows > 0 else 0,
}

# Sauvegarder le rapport
import json
report_file = f"data/processed/analysis_report_{timestamp}.json"
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2, default=str)

print(f"✓ Rapport sauvegardé: {report_file}")

# Résumé final
print("\n" + "="*60)
print("✅ NETTOYAGE ET ANALYSE TERMINÉS!")
print("="*60)
print(f"""
📊 Résumé:
  - Événements initiaux: {report['initial_events']}
  - Événements nettoyés: {report['cleaned_events']}
  - Événements supprimés: {report['events_removed']}
  - Qualité des données: {report['quality_score']:.1f}%

📁 Fichiers créés:
  - local: {csv_file}
  - local: {parquet_file}
  - MinIO: processed-data/cleaned/
  - MinIO: processed-data/enriched/
  - Rapport: {report_file}

✨ Les données sont maintenant nettoyées et analysées!
""")

print("="*60 + "\n")
