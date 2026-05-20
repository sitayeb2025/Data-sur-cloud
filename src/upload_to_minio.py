import json
import os
import boto3
from botocore.client import Config
import sys

# ── Configuration MinIO ─────────────────────────────────────────────
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS   = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET   = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET         = "arxiv-raw"

# ── Connexion ────────────────────────────────────────────────────────
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS,
    aws_secret_access_key=MINIO_SECRET,
    config=Config(signature_version='s3v4')
)

def upload_file(local_path: str, object_name: str | None = None):
    """Upload un fichier vers MinIO."""
    if object_name is None:
        object_name = os.path.basename(local_path)
    s3.upload_file(local_path, BUCKET, object_name)
    print(f"✅ Fichier complet {object_name} uploadé.")

def _upload_chunk(lines: list[str], object_name: str):
    """Upload un chunk en mémoire vers MinIO."""
    data = "".join(lines).encode('utf-8')
    s3.put_object(Bucket=BUCKET, Key=object_name, Body=data)
    print(f"✅ Chunk {object_name} uploadé ({len(lines)} articles).")

def split_and_upload(source_file: str, chunk_size: int = 10_000, prefix: str = "chunks/"):
    """Découpe et upload le fichier par morceaux."""
    with open(source_file, 'r', encoding='utf-8') as f:
        chunk = []
        chunk_idx = 1
        for line in f:
            chunk.append(line)
            if len(chunk) >= chunk_size:
                _upload_chunk(chunk, f"{prefix}chunk_{chunk_idx:03d}.json")
                chunk = []
                chunk_idx += 1
        if chunk:
            _upload_chunk(chunk, f"{prefix}chunk_{chunk_idx:03d}.json")

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "data/arxiv-raw/arxiv-cs-subset-100k.json"
    
    if not os.path.exists(source):
        print(f"❌ Fichier non trouvé : {source}")
        sys.exit(1)

    print(f"🚀 Début de l'upload vers le bucket {BUCKET}...")
    split_and_upload(source)
    print("🏁 Ingestion terminée !")