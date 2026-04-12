"""
Pipeline ETL - Transformation des données NASA EONET
Nettoyage, normalisation et enrichissement des données
"""

import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventsTransformer:
    """
    Transforme les données brutes en données exploitables
    """
    
    # Mapping des types d'événements
    EVENT_TYPE_MAPPING = {
        'Algal Bloom': 'bloom',
        'Earthquake': 'earthquake',
        'Flood': 'flood',
        'Landslide': 'landslide',
        'Snow/Ice': 'snow_ice',
        'Storm': 'storm',
        'Tropical Cyclone': 'cyclone',
        'Volcano': 'volcano',
        'Wildfire': 'wildfire'
    }
    
    def __init__(self):
        self.df = None
        self.quality_report = {}
    
    def load_data(self, events: List[Dict]) -> pd.DataFrame:
        """
        Charge les événements dans un DataFrame
        
        Args:
            events: Liste des événements
            
        Returns:
            DataFrame pandas
        """
        logger.info(f"Conversion de {len(events)} événements en DataFrame")
        self.df = pd.DataFrame(events)
        logger.info(f"Dimensions initiales: {self.df.shape}")
        return self.df
    
    def clean_data(self) -> pd.DataFrame:
        """
        Nettoyage des données:
        - Gestion des valeurs manquantes
        - Suppression des doublons
        - Conversion de types
        """
        logger.info("Nettoyage des données...")
        
        # Doublons
        duplicates_before = len(self.df)
        self.df = self.df.drop_duplicates(subset=['id'], keep='first')
        self.quality_report['duplicates_removed'] = duplicates_before - len(self.df)
        logger.info(f"  - Doublons supprimés: {self.quality_report['duplicates_removed']}")
        
        # Valeurs manquantes
        missing_before = self.df.isnull().sum().sum()
        
        # Remplissage des valeurs manquantes
        self.df['description'].fillna('N/A', inplace=True)
        # Pour latitude/longitude, ne pas supprimer les lignes - garder 0 ou NaN
        self.df['latitude'].fillna(0, inplace=True)
        self.df['longitude'].fillna(0, inplace=True)
        
        missing_after = self.df.isnull().sum().sum()
        self.quality_report['missing_values_handled'] = missing_before - missing_after
        logger.info(f"  - Valeurs manquantes traitées: {self.quality_report['missing_values_handled']}")
        
        return self.df
    
    def normalize_data(self) -> pd.DataFrame:
        """
        Normalisation des données:
        - Standardisation des types
        - Normalisation des textes
        - Validation des coordonnées
        """
        logger.info("Normalisation des données...")
        
        # Conversion des dates
        self.df['start_date'] = pd.to_datetime(self.df['start_date'], errors='coerce')
        self.df['last_update'] = pd.to_datetime(self.df['last_update'], errors='coerce')
        self.df['collection_date'] = pd.to_datetime(self.df['collection_date'])
        
        # Normalisation des types d'événements
        self.df['event_type_normalized'] = self.df['event_type'].map(
            lambda x: self.EVENT_TYPE_MAPPING.get(x, 'other')
        )
        
        # Validation des coordonnées (seulement si non-zéro)
        self.df = self.df[
            (self.df['latitude'] == 0) |  # Ou pas de coordonnée
            (self.df['longitude'] == 0) |  # Ou pas de coordonnée  
            ((self.df['latitude'].between(-90, 90)) &
             (self.df['longitude'].between(-180, 180)))
        ]
        
        # Conversion des types
        self.df['latitude'] = self.df['latitude'].astype(float)
        self.df['longitude'] = self.df['longitude'].astype(float)
        self.df['geometry_count'] = self.df['geometry_count'].astype(int)
        
        logger.info(f"  - {len(self.df)} lignes validées")
        
        return self.df
    
    def enrich_data(self) -> pd.DataFrame:
        """
        Enrichissement des données:
        - Calcul de nouvelles variables
        - Catégorisation
        - Scores de sévérité
        """
        logger.info("Enrichissement des données...")
        
        # Durée de l'événement (jours)
        self.df['duration_days'] = (
            self.df['last_update'] - self.df['start_date']
        ).dt.total_seconds() / 86400
        self.df['duration_days'] = self.df['duration_days'].fillna(0)
        
        # Jours depuis le dernier update
        now = pd.Timestamp.now(tz='UTC')  # Utiliser UTC timezone-aware
        self.df['days_since_update'] = (
            now - self.df['last_update']
        ).dt.total_seconds() / 86400
        self.df['days_since_update'] = self.df['days_since_update'].fillna(0)
        
        # Score de sévérité basé sur le type d'événement
        # Wildfires = haute, Earthquakes = très haute, Storms = moyenne, etc.
        severity_map = {
            'Wildfires': 0.85,
            'Volcanic Activity': 0.90,
            'Earthquakes': 0.88,
            'Severe Storms': 0.72,
            'Floods': 0.75,
            'Other': 0.50
        }
        
        # Attribut le score de sévérité en fonction du type d'événement
        self.df['severity_score'] = self.df['event_type'].map(severity_map).fillna(0.50)
        
        # Ajouter une variation mineure basée sur geometry_count
        if self.df['geometry_count'].max() > 0:
            geometry_factor = (self.df['geometry_count'] / self.df['geometry_count'].max()) * 0.15
            self.df['severity_score'] = (self.df['severity_score'] + geometry_factor).clip(0, 1).round(2)
        
        # Catégorisation par sévérité
        self.df['severity_category'] = pd.cut(
            self.df['severity_score'],
            bins=[0, 0.33, 0.67, 1],
            labels=['Low', 'Medium', 'High']
        )
        
        # Région géographique basée sur les coordonnées réelles
        def get_region(lat, lon):
            """Mappe les coordonnées lat/lon à des régions géographiques"""
            # Gérer les coordonnées 0,0 ou invalides
            if lat == 0 and lon == 0:
                return 'Unknown'
            
            # Cartes des régions par plages de latitude/longitude
            # Format: (lat_min, lat_max, lon_min, lon_max, nom_région)
            regions = [
                # Australasie
                (-60, -10, 110, 180, 'Australia & Oceania'),
                (-15, 5, 95, 160, 'Southeast Asia'),
                # Asie
                (5, 55, 60, 140, 'Asia & Far East'),
                (50, 85, -180, 180, 'Arctic & Far North'),
                # Americas
                (-60, 15, -120, -35, 'South America'),
                (0, 30, -100, -30, 'Central America & Caribbean'),
                (25, 50, -130, -60, 'North America'),
                # Europe & Africa
                (-35, 5, -20, 55, 'Africa'),
                (30, 75, -10, 60, 'Europe & Middle East'),
                # Default
                (-90, 90, -180, 180, 'Global')
            ]
            
            for lat_min, lat_max, lon_min, lon_max, region_name in regions:
                if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                    return region_name
            
            return 'Unknown'
        
        self.df['region'] = self.df.apply(
            lambda row: get_region(row['latitude'], row['longitude']),
            axis=1
        )
        
        logger.info(f"  - Variables enrichies ajoutées")
        
        return self.df
    
    def validate_quality(self) -> Dict:
        """
        Validation de la qualité des données
        
        Returns:
            Rapport de qualité
        """
        logger.info("Validation de qualité...")
        
        self.quality_report.update({
            'total_records': len(self.df),
            'unique_events': self.df['id'].nunique(),
            'date_range': f"{self.df['start_date'].min()} to {self.df['start_date'].max()}",
            'event_types': self.df['event_type_normalized'].unique().tolist(),
            'event_types_count': self.df['event_type_normalized'].value_counts().to_dict(),
            'geographic_coverage': f"{self.df['latitude'].min():.2f}°N to {self.df['latitude'].max():.2f}°S, "
                                   f"{self.df['longitude'].min():.2f}°E to {self.df['longitude'].max():.2f}°W",
            'null_values': self.df.isnull().sum().to_dict(),
            'data_quality_percentage': (1 - self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        })
        
        logger.info(f"  - Qualité des données: {self.quality_report['data_quality_percentage']:.2f}%")
        
        return self.quality_report
    
    def export_data(self, 
                   output_dir: str = "data/processed",
                   formats: List[str] = None) -> Dict[str, str]:
        """
        Exporte les données transformées
        
        Args:
            output_dir: Répertoire de sortie
            formats: Formats de sortie ['parquet', 'csv', 'json']
            
        Returns:
            Dictionnaire avec les chemins des fichiers exportés
        """
        if formats is None:
            formats = ['parquet', 'csv']
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exported_files = {}
        
        for fmt in formats:
            try:
                if fmt == 'parquet':
                    filepath = output_path / f"events_processed_{timestamp}.parquet"
                    self.df.to_parquet(filepath, index=False)
                    
                elif fmt == 'csv':
                    filepath = output_path / f"events_processed_{timestamp}.csv"
                    self.df.to_csv(filepath, index=False, encoding='utf-8')
                    
                elif fmt == 'json':
                    filepath = output_path / f"events_processed_{timestamp}.json"
                    self.df.to_json(filepath, orient='records', indent=2)
                
                exported_files[fmt] = str(filepath)
                logger.info(f"  ✓ Exported to {fmt}: {filepath}")
                
            except Exception as e:
                logger.error(f"  ✗ Error exporting {fmt}: {e}")
        
        return exported_files
    
    def transform(self, 
                 events: List[Dict],
                 output_dir: str = "data/processed") -> Tuple[pd.DataFrame, Dict]:
        """
        Pipeline de transformation complète
        
        Args:
            events: Événements bruts
            output_dir: Répertoire de sortie
            
        Returns:
            Tuple (DataFrame transformé, rapport de qualité)
        """
        logger.info("=" * 60)
        logger.info("Démarrage du pipeline de transformation")
        logger.info("=" * 60)
        
        # Pipeline
        self.load_data(events)
        self.clean_data()
        self.normalize_data()
        self.enrich_data()
        quality = self.validate_quality()
        self.export_data(output_dir)
        
        logger.info("=" * 60)
        logger.info("✓ Transformation complétée")
        logger.info("=" * 60)
        
        return self.df, quality


def main():
    """Test de transformation"""
    # Exemple d'utilisation
    sample_events = [
        {
            'id': 'EONET_1234',
            'title': 'Wildfire in California',
            'event_type': 'Wildfire',
            'latitude': 35.5,
            'longitude': -120.2,
            'start_date': '2024-04-01',
            'last_update': '2024-04-05',
            'geometry_count': 5
        }
    ]
    
    transformer = EventsTransformer()
    df, quality = transformer.transform(sample_events)
    
    print("\nQualité des données:")
    print(json.dumps(quality, indent=2, default=str))


if __name__ == "__main__":
    main()
