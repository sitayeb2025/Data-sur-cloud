"""
Collecteur de données NASA EONET - Événements naturels
Récupère les données en temps réel de l'API NASA Earth Observatory Network
Avec support MinIO Data Lake
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import MinIO (optionnel)
try:
    from src.storage.minio_client import MinIOClient
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    logger.warning("⚠ MinIO client non disponible. Utilisation du stockage local uniquement.")


class NASAEONETCollector:
    """
    Collecteur pour l'API NASA EONET (Earth Observatory Network)
    API: https://eonet.gsfc.nasa.gov/api/v3/events
    Supporte MinIO pour le Data Lake
    """
    
    BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
    
    def __init__(self, output_dir: str = "data/raw", use_minio: bool = True):
        """
        Initialise le collecteur NASA
        
        Args:
            output_dir: Répertoire de sortie pour les données brutes (stockage local)
            use_minio: Activer le stockage MinIO (défaut: True)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
        # Initialiser MinIO si disponible
        self.minio_client = None
        self.use_minio = use_minio and MINIO_AVAILABLE
        
        if self.use_minio:
            try:
                self.minio_client = MinIOClient()
                # Créer le bucket si nécessaire
                self.minio_client.create_bucket('raw-data')
                logger.info("✓ MinIO activé pour ce collecteur")
            except Exception as e:
                logger.warning(f"⚠ Impossible d'initialiser MinIO: {e}. Utilisation du stockage local uniquement.")
                self.use_minio = False
                self.minio_client = None
        
    def fetch_events(self, 
                    limit: int = 100,
                    days: Optional[int] = None,
                    status: str = 'all') -> Optional[Dict]:
        """
        Récupère les événements naturels de l'API NASA
        
        Args:
            limit: Nombre d'événements à récupérer
            days: Nombre de jours à remonter (None = tous les événements)
            status: 'open', 'closed', ou 'all' pour tous les événements
            
        Returns:
            Dict contenant les données ou None en cas d'erreur
        """
        try:
            params = {
                'limit': limit
            }
            
            # Ajouter le status si pas 'all'
            if status != 'all':
                params['status'] = status
            
            if days:
                since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                params['sources'] = 'InciWeb,EO'
            
            logger.info(f"Récupération des événements NASA avec params: {params}")
            
            response = self.session.get(
                self.BASE_URL,
                params=params,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Data-Pipeline)',
                    'Accept': 'application/json'
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✓ {len(data.get('events', []))} événements récupérés")
            return data
            
        except requests.RequestException as e:
            logger.error(f"✗ Erreur lors de la récupération: {e}")
            return None
    
    def parse_events(self, data: Dict) -> List[Dict]:
        """
        Parsing et nettoyage des événements
        
        Args:
            data: Dictionnaire brut de l'API
            
        Returns:
            Liste des événements parsés
        """
        events = []
        
        for event in data.get('events', []):
            try:
                # Récupérer les coordonnées de la dernière géométrie
                geometry_list = event.get('geometry', [])
                last_geometry = geometry_list[-1] if geometry_list else {}
                coordinates = last_geometry.get('coordinates', [None, None])
                
                # Extraction des informations principales
                parsed_event = {
                    'id': event.get('id'),
                    'title': event.get('title'),
                    'description': event.get('description'),
                    'event_type': event.get('categories', [{}])[0].get('title') if event.get('categories') else 'Unknown',
                    'status': event.get('status'),
                    'sources': json.dumps([s.get('url') for s in event.get('sources', [])]),
                    
                    # Dates
                    'start_date': last_geometry.get('date') if geometry_list else None,
                    'last_update': last_geometry.get('date') if geometry_list else None,
                    
                    # Localisation (dernière géométrie)
                    'latitude': coordinates[1] if len(coordinates) >= 2 else 0,
                    'longitude': coordinates[0] if len(coordinates) >= 1 else 0,
                    
                    # Métadonnées
                    'geometry_count': len(geometry_list),
                    'collection_date': datetime.now().isoformat()
                }
                
                events.append(parsed_event)
                
            except Exception as e:
                logger.warning(f"Erreur parsing événement {event.get('id')}: {e}")
                continue
        
        return events
    
    def save_raw_data(self, data: Dict) -> str:
        """
        Sauvegarde les données brutes en JSON (local + MinIO)
        
        Args:
            data: Données à sauvegarder
            
        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"nasa_events_raw_{timestamp}.json"
        
        try:
            # Sauvegarde locale
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Données brutes sauvegardées localement: {filename}")
            
            # Upload MinIO
            if self.use_minio and self.minio_client:
                object_name = f"nasa_events/raw/{timestamp}.json"
                self.minio_client.upload_json('raw-data', object_name, data)
                logger.info(f"✓ Données brutes téléchargées sur MinIO: {object_name}")
            
            return str(filename)
            
        except Exception as e:
            logger.error(f"✗ Erreur sauvegarde: {e}")
            return ""
    
    def save_parsed_data(self, events: List[Dict], 
                        format: str = 'json') -> str:
        """
        Sauvegarde les données parsées (local + MinIO)
        
        Args:
            events: Liste des événements parsés
            format: Format de sortie ('json' ou 'csv')
            
        Returns:
            Chemin du fichier sauvegardé
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            if format == 'json':
                filename = self.output_dir / f"nasa_events_parsed_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(events, f, indent=2, ensure_ascii=False)
                
                # Upload MinIO
                if self.use_minio and self.minio_client:
                    object_name = f"nasa_events/parsed/{timestamp}.json"
                    self.minio_client.upload_json('raw-data', object_name, 
                                                  {'events': events, 'count': len(events)})
                    
            elif format == 'csv':
                import csv
                filename = self.output_dir / f"nasa_events_parsed_{timestamp}.csv"
                
                if events:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=events[0].keys())
                        writer.writeheader()
                        writer.writerows(events)
                
                # Upload MinIO
                if self.use_minio and self.minio_client:
                    self.minio_client.upload_file('raw-data', 
                                                  f"nasa_events/parsed/{timestamp}.csv",
                                                  str(filename),
                                                  content_type='text/csv')
            
            logger.info(f"✓ Données parsées sauvegardées ({format}): {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"✗ Erreur sauvegarde: {e}")
            return ""
    
    def collect(self, limit: int = 5000, save: bool = True) -> Dict:
        """
        Fonction principale de collecte complète
        Collecte les événements open ET closed pour plus de données
        
        Args:
            limit: Nombre d'événements à collecter par status
            save: Si True, sauvegarde les fichiers
        
        Returns:
            Dictionnaire avec les résultats et chemins
        """
        logger.info("=" * 60)
        logger.info("Démarrage de la collecte NASA EONET (Open + Closed)")
        logger.info("=" * 60)
        
        all_events = []
        
        # Récupérer les événements open
        logger.info(f"📡 Récupération des événements OPEN (limite: {limit})...")
        raw_open = self.fetch_events(limit=limit, status='open')
        if raw_open:
            events_open = self.parse_events(raw_open)
            all_events.extend(events_open)
            logger.info(f"   ✓ {len(events_open)} événements OPEN")
        
        # Récupérer les événements closed
        logger.info(f"📡 Récupération des événements CLOSED (limite: {limit})...")
        raw_closed = self.fetch_events(limit=limit, status='closed')
        if raw_closed:
            events_closed = self.parse_events(raw_closed)
            all_events.extend(events_closed)
            logger.info(f"   ✓ {len(events_closed)} événements CLOSED")
        
        if not all_events:
            return {
                'success': False,
                'error': 'Impossible de récupérer les données'
            }
        
        logger.info(f"✓ Total: {len(all_events)} événements collectés")
        
        result = {
            'success': True,
            'events_count': len(all_events),
            'events': all_events,
            'raw_events_count': len(all_events),
            'parsed_events_count': len(all_events),
            'raw_file': '',
            'raw_json_path': '',
            'parsed_json_file': '',
            'parsed_csv_file': ''
        }
        
        # Sauvegarde optionnelle
        if save:
            # Pour la sauvegarde, combiner les données open et closed
            combined_raw = {
                'events': all_events
            }
            result['raw_file'] = self.save_raw_data(combined_raw)
            result['raw_json_path'] = result['raw_file']
            result['parsed_json_file'] = self.save_parsed_data(all_events, 'json')
            result['parsed_csv_file'] = self.save_parsed_data(all_events, 'csv')
        
        logger.info("=" * 60)
        logger.info(f"✓ Collecte terminée: {len(all_events)} événements")
        logger.info("=" * 60)
        
        return result


def main():
    """Fonction de test"""
    collector = NASAEONETCollector()
    result = collector.collect(limit=100, save=True)
    
    if result['success']:
        print(f"\n✓ Collecte réussie!")
        print(f"  Événements: {result['events_count']}")
        print(f"  Fichier brut: {result['raw_file']}")
        print(f"  Fichier JSON: {result['parsed_json_file']}")
        print(f"  Fichier CSV: {result['parsed_csv_file']}")
    else:
        print(f"\n✗ Erreur: {result.get('error')}")


if __name__ == "__main__":
    main()
