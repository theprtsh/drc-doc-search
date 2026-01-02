import pymysql
from pymysql.cursors import DictCursor
from typing import List, Dict, Any
from .log import get_logger
from .config import Config

log = get_logger()

class DatabaseManager:
    def __init__(self):
        self.conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_NAME,
            port=Config.DB_PORT,
            cursorclass=DictCursor,
            autocommit=True
        )

    def ensure_table(self, dest_table: str):
        """
        Creates the destination table (feri_docs/fere_docs) if it doesn't exist.
        """
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{dest_table}` (
            `id` int NOT NULL,
            `numero` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_unicode_ci NOT NULL,
            `date_crea` DATETIME DEFAULT NULL, 
            `scan_titre` varchar(255) DEFAULT NULL,
            `scan_titre_exist` TINYINT(1) DEFAULT 0,
            `scan_titre_path` varchar(1024) DEFAULT NULL,
            `colissage` varchar(255) DEFAULT NULL,
            `colissage_exist` TINYINT(1) DEFAULT 0,
            `colissage_path` varchar(1024) DEFAULT NULL,
            `scan_valeur` varchar(255) DEFAULT NULL,
            `scan_valeur_exist` TINYINT(1) DEFAULT 0,
            `scan_valeur_path` varchar(1024) DEFAULT NULL,
            `hostname` varchar(100) DEFAULT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            log.info(f"Ensured table exists: {dest_table}")

    def fetch_missing_rows(self, source_table: str, dest_table: str) -> List[Dict[str, Any]]:
        """
        Fetches rows from source that are NOT yet in the destination table.
        Logic: LEFT JOIN where dest.id is NULL.
        """
        # Note: We assume 'date_crea' exists in the source table based on requirements.
        sql = f"""
            SELECT 
                s.id, 
                s.numero, 
                s.date_crea, 
                s.scan_titre, 
                s.colissage, 
                s.scan_valeur 
            FROM `{source_table}` s
            LEFT JOIN `{dest_table}` d ON s.id = d.id
            WHERE d.id IS NULL
        """
        
        with self.conn.cursor() as cursor:
            log.info(f"Fetching new records from {source_table} (missing in {dest_table})...")
            cursor.execute(sql)
            rows = cursor.fetchall()
            log.info(f"Found {len(rows)} new rows to process.")
            return rows


    def close(self):
        self.conn.close()
