import pymysql
from pymysql.cursors import DictCursor
from typing import List, Dict, Any
from .log import get_logger
from .config import Config

log = get_logger()

class DatabaseManager:
    def __init__(self):

        # Connect using DEST_DB
        self.conn = pymysql.connect(
            host=Config.DEST_DB_HOST,
            user=Config.DEST_DB_USER,
            password=Config.DEST_DB_PASSWD,
            database=Config.DEST_DB_NAME,
            port=Config.DEST_DB_PORT,
            cursorclass=DictCursor,
            autocommit=True
        )
        self.src_db = Config.SRC_DB_NAME
        self.dest_db = Config.DEST_DB_NAME

    def ensure_table(self, dest_table: str):
        """
        Creates the destination table if it doesn't exist.
        """
        sql = f"""
        Creates the destination table if it doesn't exist.
        """
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.dest_db}`.`{dest_table}` (
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
        Fetches rows from source that are NOT in dest OR are in dest but marked as not found.
        """
        sql = f"""
            SELECT 
                s.id, 
                s.numero, 
                s.date_crea, 
                s.scan_titre, 
                s.colissage, 
                s.scan_valeur,
                d.scan_titre_exist,
                d.colissage_exist,
                d.scan_valeur_exist
            FROM `{self.src_db}`.`{source_table}` s
            LEFT JOIN `{self.dest_db}`.`{dest_table}` d ON s.id = d.id
            WHERE 
                d.id IS NULL 
                OR d.scan_titre_exist = 0 
                OR d.colissage_exist = 0 
                OR d.scan_valeur_exist = 0
        """
        
        with self.conn.cursor() as cursor:
            log.info(f"Fetching records to sync from {source_table}...")
            cursor.execute(sql)
            rows = cursor.fetchall()
            log.info(f"Found {len(rows)} rows to process (New + Retries).")
            return rows

    def batch_upsert(self, dest_table: str, data: List[Dict[str, Any]]):
        """
        Inserts new records or updates them
        """
        if not data:
            return

        # Columns matching the destination schema
        columns = [
            "id", "numero", "date_crea", "hostname",
            "scan_titre", "scan_titre_exist", "scan_titre_path",
            "colissage", "colissage_exist", "colissage_path",
            "scan_valeur", "scan_valeur_exist", "scan_valeur_path"
        ]
        
        # Prepare SQL statement
        placeholders = ", ".join(["%s"] * len(columns))
        col_names = ", ".join([f"`{c}`" for c in columns])
        
        # ON DUPLICATE KEY UPDATE: Update fields that might change (mostly paths/flags)
        # We exclude ID, numero, date_crea from update usually, but here we update paths/flags.
        update_clause = ", ".join([f"`{c}`=VALUES(`{c}`)" for c in columns if c not in ["id", "numero", "date_crea"]])

        sql = f"INSERT INTO `{self.dest_db}`.`{dest_table}` ({col_names}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"

        values = []
        for row in data:
            # Create a tuple in the exact order of 'columns'
            values.append(tuple(row.get(c) for c in columns))

        # Execute in batches of 1000
        batch_size = 1000
        with self.conn.cursor() as cursor:
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                cursor.executemany(sql, batch)
                log.info(f"Upserted batch {i} to {i+len(batch)} into {dest_table}")

    def close(self):
        self.conn.close()
