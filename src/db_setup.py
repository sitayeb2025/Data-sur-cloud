"""
Script de configuration de la base de données PostgreSQL
Création des schémas, tables et indexes
"""

import psycopg2
from psycopg2 import sql
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DB_HOST = os.getenv('PGHOST', 'localhost')
DB_PORT = int(os.getenv('PGPORT', 5433))
DB_NAME = os.getenv('PGDATABASE', 'events_db')
DB_USER = os.getenv('PGUSER', 'airflow')
DB_PASSWORD = os.getenv('PGPASSWORD', 'airflow')


class DatabaseSetup:
    """Configurateur de base de données"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Établit la connexion à la base de données"""
        try:
            self.connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database='postgres',  # Se connecter à la BD par défaut
                user=DB_USER,
                password=DB_PASSWORD
            )
            self.cursor = self.connection.cursor()
            logger.info("✓ Connexion établie")
        except Exception as e:
            logger.error(f"✗ Erreur connexion: {e}")
            raise
    
    def create_database(self):
        """Crée la base de données si elle n'existe pas"""
        try:
            # Configuration de psycopg2 pour ne pas faire de rollback auto
            self.connection.autocommit = True
            
            self.cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
            exists = self.cursor.fetchone()
            
            if not exists:
                self.cursor.execute(sql.SQL(f"CREATE DATABASE {DB_NAME}"))
                logger.info(f"✓ Base de données '{DB_NAME}' créée")
            else:
                logger.info(f"✓ Base de données '{DB_NAME}' existe déjà")
            
            self.connection.autocommit = False
        except Exception as e:
            logger.error(f"✗ Erreur création BDD: {e}")
            raise
    
    def connect_to_target_db(self):
        """Se connecte à la base de données cible"""
        try:
            self.connection.close()
            self.connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            self.cursor = self.connection.cursor()
            logger.info(f"✓ Connecté à '{DB_NAME}'")
        except Exception as e:
            logger.error(f"✗ Erreur connexion cible: {e}")
            raise
    
    def create_tables(self):
        """Crée les tables principales"""
        
        # Table des événements
        create_events_table = """
        CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(50) PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            event_type VARCHAR(50),
            event_type_normalized VARCHAR(50),
            status VARCHAR(20),
            
            -- Localisation
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            region VARCHAR(100),
            
            -- Dates
            start_date TIMESTAMP,
            last_update TIMESTAMP,
            collection_date TIMESTAMP DEFAULT NOW(),
            
            -- Métriques
            severity_score FLOAT,
            severity_category VARCHAR(20),
            geometry_count INTEGER,
            duration_days FLOAT,
            days_since_update FLOAT,
            
            -- Métadonnées
            sources TEXT
        );
        
        -- Créer les indexes
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type_normalized);
        CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity_score);
        CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
        CREATE INDEX IF NOT EXISTS idx_events_region ON events(region);
        CREATE INDEX IF NOT EXISTS idx_events_date ON events(start_date);
        CREATE INDEX IF NOT EXISTS idx_events_location ON events(latitude, longitude);
        """
        
        # Table des statistiques journalières
        create_stats_table = """
        CREATE TABLE IF NOT EXISTS daily_stats (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL UNIQUE,
            event_count INTEGER,
            avg_severity FLOAT,
            max_severity FLOAT,
            active_events INTEGER,
            unique_types INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);
        """
        
        # Table d'audit
        create_audit_table = """
        CREATE TABLE IF NOT EXISTS pipeline_audit (
            id SERIAL PRIMARY KEY,
            pipeline_run_id VARCHAR(100),
            status VARCHAR(20),
            events_collected INTEGER,
            events_processed INTEGER,
            events_loaded INTEGER,
            errors TEXT,
            execution_time_seconds FLOAT,
            run_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_audit_date ON pipeline_audit(run_date);
        """
        
        try:
            # Créer les tables
            self.cursor.execute(create_events_table)
            logger.info("✓ Table 'events' créée")
            
            self.cursor.execute(create_stats_table)
            logger.info("✓ Table 'daily_stats' créée")
            
            self.cursor.execute(create_audit_table)
            logger.info("✓ Table 'pipeline_audit' créée")
            
            self.connection.commit()
            logger.info("✓ Toutes les tables créées avec succès")
            
        except Exception as e:
            logger.error(f"✗ Erreur création tables: {e}")
            self.connection.rollback()
            raise
    
    def create_views(self):
        """Crée les vues SQL utiles"""
        
        views = {
            'events_active': """
            CREATE OR REPLACE VIEW events_active AS
            SELECT * FROM events
            WHERE status = 'open'
            ORDER BY severity_score DESC;
            """,
            
            'events_high_severity': """
            CREATE OR REPLACE VIEW events_high_severity AS
            SELECT * FROM events
            WHERE severity_score > 0.7
            ORDER BY severity_score DESC;
            """,
            
            'events_by_type': """
            CREATE OR REPLACE VIEW events_by_type AS
            SELECT 
                event_type_normalized,
                COUNT(*) as count,
                AVG(severity_score) as avg_severity,
                MAX(severity_score) as max_severity
            FROM events
            GROUP BY event_type_normalized
            ORDER BY count DESC;
            """,
            
            'events_by_region': """
            CREATE OR REPLACE VIEW events_by_region AS
            SELECT 
                region,
                COUNT(*) as count,
                AVG(severity_score) as avg_severity,
                COUNT(DISTINCT event_type_normalized) as unique_types
            FROM events
            GROUP BY region
            ORDER BY avg_severity DESC;
            """
        }
        
        try:
            for view_name, view_sql in views.items():
                self.cursor.execute(view_sql)
                logger.info(f"✓ Vue '{view_name}' créée")
            
            self.connection.commit()
        except Exception as e:
            logger.error(f"✗ Erreur création vues: {e}")
            self.connection.rollback()
            raise
    
    def close(self):
        """Ferme la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Connexion fermée")
    
    def setup(self):
        """Exécute l'installation complète"""
        try:
            logger.info("=" * 60)
            logger.info("Configuration PostgreSQL - Début")
            logger.info("=" * 60)
            
            self.connect()
            self.create_database()
            self.connect_to_target_db()
            self.create_tables()
            self.create_views()
            
            logger.info("=" * 60)
            logger.info("✓ Configuration terminée avec succès")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"✗ Installation échouée: {e}")
            raise
        finally:
            self.close()


def main():
    """Point d'entrée principal"""
    setup = DatabaseSetup()
    setup.setup()


if __name__ == "__main__":
    main()
