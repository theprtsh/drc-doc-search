import os
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
from .log import get_logger
from .config import Config

log = get_logger()

class FileProcessor:
    def __init__(self):
        # init DS
        # key -> fname
        # value -> list of paths
        self.file_map = defaultdict(list)

    def load_snapshots(self, snapshot_paths: List[Path]):
        """
        Reads snapshot files and builds the index.
        """
        total_lines = 0
        for snap_path in snapshot_paths:
            log.info(f"Loading snapshot: {snap_path.name}")
            try:
                with open(snap_path, "r", encoding="utf-8") as f:
                    for line in f:
                        full_path = line.strip()
                        if not full_path:
                            continue
                        
                        # path -> fname
                        fname = os.path.basename(full_path).lower()
                        
                        # Store the FULL path in the list
                        self.file_map[fname].append(full_path)
                        total_lines += 1
            except FileNotFoundError:
                log.error(f"Snapshot file not found: {snap_path}")

        log.info(f"Indexed {total_lines} paths. Unique filenames: {len(self.file_map)}")

    def match_records(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Iterates through DB rows and finds matching files in the index.
        """
        processed_rows = []
        host_str = Config.SSH_HOST if Config.SSH_HOST else "local"

        for row in rows:
            # Set host
            row["hostname"] = host_str

            # Check each file column
            self._enrich_row(row, "scan_titre", "scan_titre_exist", "scan_titre_path")
            self._enrich_row(row, "colissage", "colissage_exist", "colissage_path")
            self._enrich_row(row, "scan_valeur", "scan_valeur_exist", "scan_valeur_path")

            processed_rows.append(row)
        
        return processed_rows

    def _enrich_row(self, row: Dict, filename_key: str, exist_key: str, path_key: str):
        """
        Helper logic:
        1. Checks if we already found it (exist != 0).
        2. Cleans DB filename.
        3. Looks up in file_map.
        4. Joins multiple paths with comma if found.
        """
        current_exist = row.get(exist_key)
        
        # If marked 1 skip
        # 0 -> Not Found Yet.
        if current_exist and current_exist != 0:
            return

        # Get filename from DB
        filename = row.get(filename_key)
        
        if filename and isinstance(filename, str) and filename.strip():
            # Lowercase to match the index
            clean_name = filename.strip().lower()
            
            # Lookup
            found_paths = self.file_map.get(clean_name)
            
            if found_paths:
                row[exist_key] = 1
                row[path_key] = ",".join(found_paths)
            else:
                row[exist_key] = 0
                row[path_key] = None
        else:
            # Handle empty/None filename in DB
            row[exist_key] = 0
            row[path_key] = None
