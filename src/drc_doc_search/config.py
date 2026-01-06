import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Config:
    # Source DB
    SRC_DB_NAME = os.getenv("SRC_DB")
    SRC_DB_USER = os.getenv("SRC_DB_USER", "root")
    SRC_DB_PASSWD = os.getenv("SRC_DB_PASSWD", "passwd")
    SRC_DB_HOST = os.getenv("SRC_DB_HOST", "localhost")
    SRC_DB_PORT = int(os.getenv("SRC_DB_PORT", 3306))

    # Destination DB
    DEST_DB_NAME = os.getenv("DEST_DB")
    DEST_DB_USER = os.getenv("DEST_DB_USER", "root")
    DEST_DB_PASSWD = os.getenv("DEST_DB_PASSWD", "passwd")
    DEST_DB_HOST = os.getenv("DEST_DB_HOST", "localhost")
    DEST_DB_PORT = int(os.getenv("DEST_DB_PORT", 3306))

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
