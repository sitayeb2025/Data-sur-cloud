#!/usr/bin/env python3
"""
Diagnostic MinIO + Collecte NASA EONET
- Vérifie la connexion MinIO
- Crée les buckets nécessaires
- Collecte les données NASA EONET
- Upload vers MinIO
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
MINIO_ENDPOINT   = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKETS_NEEDED   = ["raw-data", "processed-data"]

def check_env():
    """Charge les variables d'environnement si .env existe"""
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        endpoint   = os.getenv("MINIO_ENDPOINT",   MINIO_ENDPOINT)
        access_key = os.getenv("MINIO_ACCESS_KEY", MINIO_ACCESS_KEY)
        secret_key = os.getenv("MINIO_SECRET_KEY", MINIO_SECRET_KEY)
        return endpoint, access_key, secret_key
    except Exception:
        return MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY


def diagnostic_minio(endpoint, access_key, secret_key):
    """Vérifie MinIO et crée les buckets manquants"""
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC MINIO")
    print("="*60)

    try:
        from minio import Minio
        client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)

        print(f"✔ Connexion à MinIO : {endpoint}")

        for bucket in BUCKETS_NEEDED:
            if client.bucket_exists(bucket):
                print(f"✔ Bucket '{bucket}' existe déjà")
            else:
                client.make_bucket(bucket)
                print(f"✔ Bucket '{bucket}' créé")

        print("✔ MinIO opérationnel\n")
        return client

    except Exception as e:
        print(f"✗ Erreur MinIO : {e}")
        print("  Vérifiez que les containers Docker tournent (docker ps)")
        sys.exit(1)


def collect_nasa(client):
    """Collecte les données NASA EONET et les upload dans MinIO"""
    print("="*60)
    print("🛰️  COLLECTE NASA EONET")
    print("="*60)

    try:
        from src.collectors.nasa_collector import NASAEONETCollector

        collector = NASAEONETCollector(output_dir="data/raw", use_minio=True)
        print("✔ Collecteur NASA initialisé")

        print("📡 Récupération des événements (open + closed)...")
        result = collector.collect(limit=500, save=True)

        if not result.get("success"):
            print(f"✗ Échec collecte : {result.get('error')}")
            sys.exit(1)

        count = result["events_count"]
        print(f"✔ {count} événements collectés")
        print(f"  Fichier brut  : {result.get('raw_file', 'N/A')}")
        print(f"  Fichier JSON  : {result.get('parsed_json_file', 'N/A')}")
        print(f"  Fichier CSV   : {result.get('parsed_csv_file', 'N/A')}")

        return result

    except ImportError as e:
        print(f"✗ Import manquant : {e}")
        print("  Vérifiez que src/collectors/nasa_collector.py est accessible")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erreur collecte : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def verify_upload(client):
    """Vérifie que les données sont bien dans MinIO"""
    print("\n" + "="*60)
    print("📁 VÉRIFICATION CONTENU MINIO")
    print("="*60)

    for bucket in BUCKETS_NEEDED:
        try:
            objects = list(client.list_objects(bucket, recursive=True))
            print(f"\n  Bucket '{bucket}' : {len(objects)} fichier(s)")
            for obj in objects[:5]:  # Afficher les 5 premiers
                print(f"    - {obj.object_name} ({obj.size} bytes)")
            if len(objects) > 5:
                print(f"    ... et {len(objects) - 5} autre(s)")
        except Exception as e:
            print(f"  ✗ Erreur lecture bucket '{bucket}' : {e}")


def main():
    print("\n" + "🚀"*30)
    print("\n📊 DIAGNOSTIC MINIO + COLLECTE NASA")
    print("\n" + "🚀"*30 + "\n")

    # 1. Charger config
    endpoint, access_key, secret_key = check_env()

    # 2. Diagnostic MinIO + création buckets
    client = diagnostic_minio(endpoint, access_key, secret_key)

    # 3. Collecte NASA
    result = collect_nasa(client)

    # 4. Vérification
    verify_upload(client)

    # 5. Résumé
    print("\n" + "="*60)
    print("✅ DIAGNOSTIC ET COLLECTE TERMINÉS")
    print("="*60)
    print(f"  Événements collectés : {result['events_count']}")
    print(f"  Buckets MinIO        : {', '.join(BUCKETS_NEEDED)}")
    print(f"  Données locales      : data/raw/")
    print("\n  Vous pouvez maintenant lancer :")
    print("  > python clean_and_analyze_data.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()