"""
Client MinIO pour gestion du Data Lake
Gère la connexion et les opérations avec MinIO
"""

import os
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import logging
from io import BytesIO
import json

logger = logging.getLogger(__name__)


class MinIOClient:
    """Client pour gérer le Data Lake MinIO"""
    
    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        secure: bool = False
    ):
        """
        Initialise la connexion MinIO
        
        Args:
            endpoint: URL MinIO (ex: localhost:9000)
            access_key: Clé d'accès MinIO
            secret_key: Clé secrète MinIO
            secure: Utiliser HTTPS (défaut: False)
        """
        # Utiliser les variables d'environnement par défaut
        self.endpoint = endpoint or os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = access_key or os.getenv('MINIO_ROOT_USER', 'admin')
        self.secret_key = secret_key or os.getenv('MINIO_ROOT_PASSWORD', 'password')
        self.secure = secure
        
        try:
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            logger.info(f"✓ Connecté à MinIO: {self.endpoint}")
        except Exception as e:
            logger.error(f"✗ Erreur connexion MinIO: {e}")
            raise
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """Vérifie si un bucket existe"""
        try:
            return self.client.bucket_exists(bucket_name)
        except Exception as e:
            logger.error(f"✗ Erreur vérification bucket {bucket_name}: {e}")
            return False
    
    def create_bucket(self, bucket_name: str) -> bool:
        """Crée un bucket s'il n'existe pas"""
        try:
            if not self.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"✓ Bucket créé: {bucket_name}")
                return True
            else:
                logger.info(f"℃ Bucket existe déjà: {bucket_name}")
                return True
        except S3Error as e:
            logger.error(f"✗ Erreur création bucket {bucket_name}: {e}")
            return False
    
    def upload_file(self, bucket: str, object_name: str, file_path: str, content_type: str = "application/octet-stream") -> bool:
        """
        Upload un fichier vers MinIO
        
        Args:
            bucket: Nom du bucket
            object_name: Chemin de l'objet dans MinIO
            file_path: Chemin du fichier local
            content_type: Type MIME du fichier
        """
        try:
            if not Path(file_path).exists():
                logger.error(f"✗ Fichier n'existe pas: {file_path}")
                return False
            
            self.client.fput_object(
                bucket,
                object_name,
                file_path,
                content_type=content_type
            )
            logger.info(f"✓ Fichier uploadé: {bucket}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"✗ Erreur upload: {e}")
            return False
    
    def upload_json(self, bucket: str, object_name: str, data: dict) -> bool:
        """Upload des données JSON"""
        try:
            json_bytes = json.dumps(data, indent=2).encode('utf-8')
            self.client.put_object(
                bucket,
                object_name,
                BytesIO(json_bytes),
                len(json_bytes),
                content_type='application/json'
            )
            logger.info(f"✓ JSON uploadé: {bucket}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"✗ Erreur upload JSON: {e}")
            return False
    
    def download_file(self, bucket: str, object_name: str, file_path: str) -> bool:
        """Télécharge un fichier depuis MinIO"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            self.client.fget_object(bucket, object_name, file_path)
            logger.info(f"✓ Fichier téléchargé: {bucket}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"✗ Erreur téléchargement: {e}")
            return False
    
    def get_json(self, bucket: str, object_name: str) -> dict:
        """Récupère et parse un JSON depuis MinIO"""
        try:
            response = self.client.get_object(bucket, object_name)
            data = json.loads(response.read().decode('utf-8'))
            logger.info(f"✓ JSON récupéré: {bucket}/{object_name}")
            return data
        except Exception as e:
            logger.error(f"✗ Erreur récupération JSON: {e}")
            return None
    
    def list_objects(self, bucket: str, prefix: str = "") -> list:
        """Liste les objets d'un bucket"""
        try:
            objects = self.client.list_objects(bucket, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"✗ Erreur listing: {e}")
            return []
    
    def delete_object(self, bucket: str, object_name: str) -> bool:
        """Supprime un objet"""
        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"✓ Objet supprimé: {bucket}/{object_name}")
            return True
        except S3Error as e:
            logger.error(f"✗ Erreur suppression: {e}")
            return False


def init_buckets():
    """Initialise les buckets MinIO par défaut"""
    client = MinIOClient()
    buckets = [
        'raw-data',      # Données brutes de collecte
        'processed-data',  # Données traitées
        'models',        # Modèles ML
        'reports'        # Rapports et exports
    ]
    
    for bucket in buckets:
        client.create_bucket(bucket)
    
    return client
