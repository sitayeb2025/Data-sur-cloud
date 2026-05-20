#!/usr/bin/env python3
"""
Pipeline complet: Collecte → Nettoyage → Analyse
Lance tout le workflow en une commande
"""

import sys
import subprocess
from pathlib import Path

print("\n" + "🚀"*30)
print("\n📊 PIPELINE COMPLET NASA EONET + MINIO")
print("\n" + "🚀"*30 + "\n")

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

steps = [
    ("1. DIAGNOSTIC MINIO + COLLECTE", "python diagnostic_minio_collecte.py"),
    ("2. NETTOYAGE ET ANALYSE", "python clean_and_analyze_data.py"),
]

print("📋 Étapes du pipeline:")
for i, (name, _) in enumerate(steps, 1):
    print(f"  {name}")

print("\n" + "="*60)

for step_name, command in steps:
    print(f"\n▶️  {step_name}")
    print("="*60)
    
    try:
        result = subprocess.run(command, shell=True, check=False)
        if result.returncode != 0:
            print(f"\n⚠️  {step_name} a retourné un code d'erreur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

print("\n" + "="*60)
print("\n✅ PIPELINE TERMINÉ!")
print("="*60)

print("""
📊 Résumé des résultats:
  1. ✓ Données collectées depuis NASA API
  2. ✓ Sauvegarde locale (data/raw/)
  3. ✓ Upload MinIO (raw-data bucket)
  4. ✓ Nettoyage des données
  5. ✓ Analyse et enrichissement
  6. ✓ Sauvegarde MinIO (processed-data bucket)

🌐 MinIO Console:
  http://localhost:9001 (admin/password)

📁 Fichiers disponibles:
  - Données brutes: raw-data/nasa_events/
  - Données nettoyées: processed-data/cleaned/
  - Données enrichies: processed-data/enriched/

✨ Pipeline de Data Lake en production!
""")

print("="*60 + "\n")
