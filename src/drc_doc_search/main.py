import sys
from .log import get_logger
from .remote import RemoteScanner

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


    log.info("Sync process finished successfully.")

if __name__ == "__main__":
    main()
