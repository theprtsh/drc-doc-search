import sys
from .log import get_logger
from .remote import RemoteScanner
from .db import DatabaseManager
from .config import Config

log = get_logger()

def main():
    log.info("Starting sync process...")

    # 1. Generate Remote Snapshots (Returns a List of paths)
    scanner = RemoteScanner()
    try:
        snapshot_files = scanner.generate_snapshots()
    except Exception as e:
        log.critical(f"Failed to get remote snapshots: {e}")
        sys.exit(1)

    db = DatabaseManager()
    
    try:
        for source_table, dest_table in Config.TABLE_MAP.items():
            log.info(f"--- Processing {source_table} -> {dest_table} ---")
            
            # Ensure destination table exists
            db.ensure_table(dest_table)
            
            # Fetch source data
            rows = db.fetch_missing_rows(source_table, dest_table)
            if not rows:
                log.warning(f"No data found in {source_table}")
                continue
            
            # Match data in memory
            log.info(f"Matching {len(rows)} records against file index...")
            # enriched_data = processor.match_records(rows)
            
            # Save back to DB
            db.batch_upsert(dest_table, rows)
            
    finally:
        db.close()


    log.info("Sync process finished successfully.")

if __name__ == "__main__":
    main()
