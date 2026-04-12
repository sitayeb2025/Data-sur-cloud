"""
Collecteur de tremblements de terre (Earthquakes)
Se connecte à l'API USGS pour récupérer les données sismiques
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class USGSEarthquakeCollector:
    """
    Collecteur pour l'API USGS (United States Geological Survey)
    API: https://earthquake.usgs.gov/fdsnws/event/1/query
    """
    
    BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    def __init__(self, output_dir: str = "data/raw"):
        """
        Initialise le collecteur d'earthquakes
        
        Args:
            output_dir: Répertoire de sortie pour les données brutes
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
    def fetch_earthquakes(self, 
                         limit: int = 5000,
                         min_magnitude: float = 4.0,
                         days: Optional[int] = None) -> Optional[Dict]:
        """
        Récupère les tremblements de terre de l'API USGS
        
        Args:
            limit: Nombre d'événements à récupérer
            min_magnitude: Magnitude minimum
            days: Nombre de jours à remonter
            
        Returns:
            Dict contenant les données ou None en cas d'erreur
        """
        try:
            # Calculer la date de début
            if days:
                start_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
            else:
                start_date = '2024-01-01'  # Données récentes seulement
            
            params = {
                'format': 'geojson',
                'starttime': start_date,
                'minmagnitude': min_magnitude,
                'limit': min(limit, 20000)  # USGS a une limite de 20000
            }
            
            logger.info(f"Récupération des tremblements de terre USGS: magnitude >= {min_magnitude}, depuis {start_date}")
            
            response = self.session.get(
                self.BASE_URL,
                params=params,
                headers={'User-Agent': 'Data-Pipeline'},
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            count = len(data.get('features', []))
            logger.info(f"✓ {count} tremblements de terre récupérés")
            return data
            
        except Exception as e:
            logger.error(f"✗ Erreur récupération: {e}")
            return None
    
    def parse_earthquakes(self, data: Dict) -> List[Dict]:
        """
        Parse les données USGS en format standardisé
        
        Args:
            data: Données brutes de l'API USGS
            
        Returns:
            Liste des événements parsés
        """
        events = []
        
        for feature in data.get('features', []):
            try:
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [None, None, None])
                
                parsed_event = {
                    'id': props.get('ids', '').split(',')[0] if props.get('ids') else f"usgs_{props.get('code')}",
                    'title': props.get('title', 'Earthquake'),
                    'description': f"Magnitude {props.get('mag', 'N/A')} - {props.get('place', 'Unknown')}",
                    'event_type': 'Earthquakes',
                    'status': 'open',
                    'sources': json.dumps([props.get('url', '')]) if props.get('url') else '[]',
                    
                    # Dates
                    'start_date': datetime.utcfromtimestamp(props['time']/1000).isoformat() if 'time' in props else None,
                    'last_update': datetime.utcfromtimestamp(props['updated']/1000).isoformat() if 'updated' in props else None,
                    
                    # Localisation
                    'latitude': coords[1] if len(coords) >= 2 else 0,
                    'longitude': coords[0] if len(coords) >= 1 else 0,
                    
                    # Métadonnées
                    'geometry_count': 1,
                    'collection_date': datetime.utcnow().isoformat(),
                    
                    # Données supplémentaires
                    'magnitude': props.get('mag', 0),
                    'depth': coords[2] if len(coords) >= 3 else 0,
                    'felt_reports': props.get('felt', 0),
                    'tsunami': props.get('tsunami', 0)
                }
                
                events.append(parsed_event)
                
            except Exception as e:
                logger.warning(f"Erreur parsing : {e}")
                continue
        
        return events
    
    def save_data(self, events: List[Dict]) -> str:
        """
        Sauvegarde les tremblements de terre en JSON
        
        Args:
            events: Événements à sauvegarder
            
        Returns:
            Chemin du fichier
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"usgs_earthquakes_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Sauvegardé: {filename}")
            return str(filename)
        except Exception as e:
            logger.error(f"✗ Erreur sauvegarde: {e}")
            return ""
    
    def collect(self, limit: int = 5000, min_magnitude: float = 4.0) -> Dict:
        """
        Collecte complète des tremblements de terre
        
        Args:
            limit: Nombre maximum d'événements
            min_magnitude: Magnitude minimale
            
        Returns:
            Résultat de la collecte
        """
        logger.info("=" * 60)
        logger.info("Collecte des tremblements de terre USGS")
        logger.info("=" * 60)
        
        # Récupération
        raw_data = self.fetch_earthquakes(limit=limit, min_magnitude=min_magnitude)
        if not raw_data:
            return {
                'success': False,
                'error': 'Impossible de récupérer les données'
            }
        
        # Parse
        earthquakes = self.parse_earthquakes(raw_data)
        logger.info(f"✓ {len(earthquakes)} tremblements de terre parsés")
        
        result = {
            'success': True,
            'events_count': len(earthquakes),
            'events': earthquakes
        }
        
        # Sauvegarde
        result['file'] = self.save_data(earthquakes)
        
        logger.info("=" * 60)
        logger.info(f"✓ Collecte complétée: {len(earthquakes)} tremblements de terre")
        logger.info("=" * 60)
        
        return result
