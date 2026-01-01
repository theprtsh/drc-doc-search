import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # DB
    DB_NAME = os.getenv("DB")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASSWD", "passwd")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))

    # SSH
    SSH_HOST = os.getenv("SSH_HOST")
    SSH_USER = os.getenv("SSH_USER", "ubuntu")

    # Resolve absolute path to SSH key
    SSH_KEY_PATH = str(BASE_DIR / "ssh.key")

    # Mappings
    TABLE_MAP = {
        "feri": "feri_docs",
        "fere": "fere_docs"
    }

    REMOTE_PATHS = [
        "/app/data/continuite",
        "/app/amazon/continuite"
    ]
    
    # Local path to store snapshots
    SNAPSHOT_DIR = BASE_DIR / "snapshots"
