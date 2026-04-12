"""
Scripts d'analyse des événements NASA EONET
Analyses statistiques et exploratoires
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration des styles
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)


class EventsAnalyzer:
    """Analyseur statistique des événements"""
    
    def __init__(self, data_path: str = None):
        """
        Initialise l'analyseur
        
        Args:
            data_path: Chemin vers le fichier de données
        """
        self.df = None
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, data_path: str) -> pd.DataFrame:
        """Charge les données processées"""
        logger.info(f"Chargement: {data_path}")
        
        if data_path.endswith('.parquet'):
            self.df = pd.read_parquet(data_path)
        elif data_path.endswith('.csv'):
            self.df = pd.read_csv(data_path)
        else:
            raise ValueError("Format non supporté")
        
        # Conversion des dates
        for col in ['start_date', 'last_update', 'collection_date']:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col])
        
        logger.info(f"✓ {len(self.df)} événements chargés")
        return self.df
    
    def descriptive_stats(self) -> dict:
        """Statistiques descriptives"""
        if self.df is None:
            return {}
        
        stats = {
            'total_events': len(self.df),
            'unique_events': self.df['id'].nunique(),
            'date_range': {
                'start': self.df['start_date'].min(),
                'end': self.df['start_date'].max()
            },
            'geographic_coverage': {
                'lat_range': [self.df['latitude'].min(), self.df['latitude'].max()],
                'lon_range': [self.df['longitude'].min(), self.df['longitude'].max()]
            },
            'severity_stats': {
                'mean': self.df['severity_score'].mean(),
                'median': self.df['severity_score'].median(),
                'std': self.df['severity_score'].std(),
                'min': self.df['severity_score'].min(),
                'max': self.df['severity_score'].max()
            },
            'event_types': self.df['event_type_normalized'].value_counts().to_dict(),
            'status_distribution': self.df['status'].value_counts().to_dict(),
        }
        
        logger.info("Statistiques descriptives calculées")
        return stats
    
    def event_type_analysis(self) -> dict:
        """Analyse par type d'événement"""
        analysis = {}
        
        for event_type in self.df['event_type_normalized'].unique():
            subset = self.df[self.df['event_type_normalized'] == event_type]
            analysis[event_type] = {
                'count': len(subset),
                'avg_severity': subset['severity_score'].mean(),
                'avg_duration': subset['duration_days'].mean(),
                'locations': subset['region'].nunique()
            }
        
        return analysis
    
    def geographic_analysis(self) -> dict:
        """Analyse géographique"""
        analysis = {}
        
        for region in self.df['region'].unique():
            subset = self.df[self.df['region'] == region]
            analysis[region] = {
                'count': len(subset),
                'avg_severity': subset['severity_score'].mean(),
                'event_types': subset['event_type_normalized'].nunique(),
                'events': subset['event_type_normalized'].unique().tolist()
            }
        
        return analysis
    
    def temporal_analysis(self) -> pd.DataFrame:
        """Analyse temporelle"""
        self.df['date'] = self.df['start_date'].dt.date
        
        temporal = self.df.groupby('date').agg({
            'id': 'count',
            'severity_score': 'mean',
            'event_type_normalized': 'nunique'
        }).rename({
            'id': 'event_count',
            'event_type_normalized': 'unique_types'
        }, axis=1)
        
        return temporal
    
    def anomaly_detection(self, severity_threshold: float = 0.75) -> pd.DataFrame:
        """Détecte les anomalies/événements de haute sévérité"""
        anomalies = self.df[self.df['severity_score'] >= severity_threshold][
            ['id', 'title', 'event_type_normalized', 'severity_score', 'latitude', 'longitude', 'start_date']
        ].sort_values('severity_score', ascending=False)
        
        logger.info(f"✓ {len(anomalies)} événements détectés avec sévérité >= {severity_threshold}")
        return anomalies
    
    def plot_severity_distribution(self, save_path: str = None):
        """Visualise la distribution de sévérité"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogramme
        axes[0].hist(self.df['severity_score'], bins=30, color='steelblue', alpha=0.7, edgecolor='black')
        axes[0].set_xlabel('Score de Sévérité')
        axes[0].set_ylabel('Fréquence')
        axes[0].set_title('Distribution de la Sévérité')
        axes[0].grid(True, alpha=0.3)
        
        # Box plot par catégorie
        self.df.boxplot(column='severity_score', by='severity_category', ax=axes[1])
        axes[1].set_xlabel('Catégorie de Sévérité')
        axes[1].set_ylabel('Score')
        axes[1].set_title('Sévérité par Catégorie')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            logger.info(f"✓ Graphique sauvegardé: {save_path}")
        
        return fig
    
    def plot_events_by_type(self, save_path: str = None):
        """Visualise les événements par type"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        event_counts = self.df['event_type_normalized'].value_counts()
        event_counts.plot(kind='barh', ax=ax, color='coral')
        
        ax.set_xlabel('Nombre d\'événements')
        ax.set_title('Événements par Type')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            logger.info(f"✓ Graphique sauvegardé: {save_path}")
        
        return fig
    
    def plot_temporal_trends(self, save_path: str = None):
        """Visualise les tendances temporelles"""
        temporal = self.temporal_analysis()
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 8))
        
        # nombre d'événements
        temporal['event_count'].plot(ax=axes[0], marker='o', color='steelblue', linewidth=2)
        axes[0].set_ylabel('Nombre d\'événements')
        axes[0].set_title('Tendance: Nombre d\'Événements par Jour')
        axes[0].grid(True, alpha=0.3)
        
        # Sévérité moyenne
        temporal['severity_score'].plot(ax=axes[1], marker='o', color='orange', linewidth=2)
        axes[1].set_ylabel('Sévérité Moyenne')
        axes[1].set_xlabel('Date')
        axes[1].set_title('Tendance: Sévérité Moyenne par Jour')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            logger.info(f"✓ Graphique sauvegardé: {save_path}")
        
        return fig
    
    def plot_geographic_heatmap(self, save_path: str = None):
        """Heatmap géographique simple"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        scatter = ax.scatter(
            self.df['longitude'],
            self.df['latitude'],
            c=self.df['severity_score'],
            s=self.df['geometry_count'] * 10,
            cmap='RdYlGn_r',
            alpha=0.6,
            edgecolors='black',
            linewidth=0.5
        )
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Carte de Densité et Sévérité des Événements')
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Sévérité')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150)
            logger.info(f"✓ Graphique sauvegardé: {save_path}")
        
        return fig
    
    def generate_report(self, output_dir: str = "reports") -> dict:
        """Génère un rapport complet d'analyse"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Génération du rapport d'analyse...")
        
        report = {
            'descriptive_stats': self.descriptive_stats(),
            'event_type_analysis': self.event_type_analysis(),
            'geographic_analysis': self.geographic_analysis(),
            'anomalies': self.anomaly_detection().to_dict('records')
        }
        
        # Sauvegarder en JSON
        import json
        report_file = output_path / "analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Créer les visualisations
        self.plot_severity_distribution(output_path / "severity_distribution.png")
        self.plot_events_by_type(output_path / "events_by_type.png")
        self.plot_temporal_trends(output_path / "temporal_trends.png")
        self.plot_geographic_heatmap(output_path / "geographic_heatmap.png")
        
        logger.info(f"✓ Rapport généré dans {output_dir}")
        
        return report


def main():
    """Exemple d'utilisation"""
    # Chercher le dernier fichier de données
    data_dir = Path("data/processed")
    parquet_files = list(data_dir.glob("events_processed_*.parquet"))
    
    if not parquet_files:
        logger.error("Aucun fichier de données trouvé")
        return
    
    latest_file = max(parquet_files, key=lambda p: p.stat().st_mtime)
    
    # Analyse
    analyzer = EventsAnalyzer(str(latest_file))
    
    # Rapport complet
    report = analyzer.generate_report(output_dir="reports")
    
    # Afficher résumé
    stats = report['descriptive_stats']
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ D'ANALYSE")
    print("=" * 60)
    print(f"Total événements: {stats['total_events']}")
    print(f"Sévérité moyenne: {stats['severity_stats']['mean']:.2f}")
    print(f"Types d'événements: {len(stats['event_types'])}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
