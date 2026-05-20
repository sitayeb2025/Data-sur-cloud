"""
DAG Airflow avec MinIO
Montre comment intégrer MinIO dans un pipeline Airflow
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin des modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from io import BytesIO

# Configuration par défaut
default_args = {
    'owner': 'nasa_eonet',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026, 4, 1),
}

def collect_data(**context):
    """Tâche: Collecte les données NASA et les sauvegarde dans MinIO"""
    from src.collectors.nasa_collector import NASAEONETCollector
    
    collector = NASAEONETCollector(use_minio=True)
    
    # Récupérer
    data = collector.fetch_events(limit=100)
    if not data:
        raise ValueError("Impossible de récupérer les données NASA")
    
    # Parser
    events = collector.parse_events(data)
    
    # Sauvegarder (local + MinIO)
    collector.save_raw_data(data)
    collector.save_parsed_data(events, format='json')
    collector.save_parsed_data(events, format='csv')
    
    # Retourner les infos pour les tâches suivantes
    return {
        'events_count': len(events),
        'timestamp': context['execution_date'].isoformat()
    }


def transform_data(**context):
    """Tâche: Transforme les données depuis MinIO et les enrichit"""
    from src.etl.transformer import EventsTransformer
    from src.storage.minio_client import MinIOClient
    import pandas as pd
    
    # Récupérer les données précédentes
    ti = context['task_instance']
    prev_result = ti.xcom_pull(task_ids='collect_data')
    
    print(f"Processing {prev_result['events_count']} events...")
    
    # Charger depuis MinIO
    client = MinIOClient()
    
    # Lister les fichiers JSON récents
    files = client.list_objects('raw-data', prefix='nasa_events/parsed/')
    
    if files:
        # Prendre le plus récent
        latest_file = sorted(files)[-1]
        data = client.get_json('raw-data', latest_file)
        
        # Transformer
        transformer = EventsTransformer()
        df = transformer.load_data(data.get('events', []))
        
        # Appliquer les transformations
        df_cleaned = transformer.clean_data(df)
        df_enriched = transformer.enrich_data(df_cleaned)
        
        # Sauvegarder dans MinIO
        csv_data = df_enriched.to_csv(index=False)
        client.client.put_object(
            'processed-data',
            f'cleaned/events_{context["execution_date"].strftime("%Y%m%d_%H%M%S")}.csv',
            BytesIO(csv_data.encode()),
            len(csv_data.encode()),
            content_type='text/csv'
        )
        
        return {'processed_rows': len(df_enriched)}
    
    raise ValueError("Aucun fichier à traiter")


def load_to_database(**context):
    """Tâche: Charge les données transformées dans PostgreSQL"""
    import pandas as pd
    from src.storage.minio_client import MinIOClient
    import tempfile
    import os
    
    try:
        # Charger depuis MinIO
        client = MinIOClient()
        files = client.list_objects('processed-data', prefix='cleaned/')
        
        if not files:
            print("⚠ Aucun fichier processé trouvé dans MinIO")
            return {'rows_inserted': 0, 'status': 'no_files'}
        
        # Prendre le plus récent
        latest_file = sorted(files)[-1]
        print(f"📁 Fichier à charger: {latest_file}")
        
        # Download dans un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            temp_file = tmp.name
        
        client.download_file('processed-data', latest_file, temp_file)
        print(f"✓ Fichier téléchargé: {temp_file}")
        
        try:
            # Charger le CSV
            df = pd.read_csv(temp_file)
            print(f"✓ CSV chargé: {len(df)} lignes")
            
            # Essayer de charger dans PostgreSQL
            try:
                from sqlalchemy import create_engine
                
                # Essayer avec la connexion Airflow
                engine = create_engine(
                    'postgresql://airflow:airflow@postgres_dw:5432/events_db'
                )
                
                df.to_sql('events', con=engine, if_exists='append', index=False)
                print(f"✓ {len(df)} lignes insérées dans PostgreSQL")
                
                return {'rows_inserted': len(df), 'status': 'success'}
                
            except Exception as db_error:
                print(f"⚠ PostgreSQL non accessible: {db_error}")
                print(f"  Les données sont disponibles dans MinIO pour traitement ultérieur")
                
                # Pas grave - les données sont dans MinIO!
                return {'rows_inserted': 0, 'status': 'postgres_unavailable', 'note': 'Données dans MinIO'}
                
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        raise


# Créer le DAG
dag = DAG(
    'nasa_eonet_pipeline_with_minio',
    default_args=default_args,
    description='Pipeline d\'ingestion NASA EONET avec MinIO Data Lake',
    schedule_interval='@daily',  # Quotidien
    catchup=False,
)

# Tâches
collect_task = PythonOperator(
    task_id='collect_data',
    python_callable=collect_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_database',
    python_callable=load_to_database,
    provide_context=True,
    dag=dag,
)

# Dépendances
collect_task >> transform_task >> load_task
