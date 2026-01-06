import sys
from .log import get_logger
from .scanner import RemoteScanner, LocalScanner, Scanner
from .db import DatabaseManager
from .processor import FileProcessor
from .config import Config

log = get_logger()

def run_sync(scanner: Scanner):
    log.info("Starting sync process...")

    # Generate Snapshots
    try:
        snapshot_files = scanner.generate_snapshots()
    except Exception as e:
        log.critical(f"Failed to generate snapshots: {e}")
        sys.exit(1)

    # 2. Load Snapshots into Memory (Processor)
    processor = FileProcessor()
    processor.load_snapshots(snapshot_files)

    # 3. DB Operations
    db = DatabaseManager()
    
    try:
        for source_table, dest_table in Config.TABLE_MAP.items():
            log.info(f"--- Processing {source_table} -> {dest_table} ---")
            
            # Ensure destination table exists
            db.ensure_table(dest_table)
            
            # Fetch source data (Only missing rows for now)
            rows = db.fetch_missing_rows(source_table, dest_table)
            
            if not rows:
                log.warning(f"No new data found in {source_table}")
                continue
            
            # Match data in memory
            log.info(f"Matching {len(rows)} records against file index...")
            
            # This updates the 'rows' list with paths and exist flags
            enriched_data = processor.match_records(rows)
            
            # Save back to DB
            db.batch_upsert(dest_table, enriched_data)
            
    finally:
        db.close()

    log.info("Sync process finished successfully.")

def main_remote():
    log.info("Mode: Remote Sync")
    scanner = RemoteScanner()
    run_sync(scanner)

def main_local():
    log.info("Mode: Local Sync")
    scanner = LocalScanner()
    run_sync(scanner)

# default
if __name__ == "__main__":
    main_local()
