import subprocess
from pathlib import Path
from typing import List
from .log import get_logger
from .config import Config

log = get_logger()

class RemoteScanner:
    def generate_snapshots(self) -> List[Path]:
        """
        Runs a single ssh command for ALL configured paths at once.
        Returns a list containing the single snapshot file.
        """
        Config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        
        # 1. Construct a single filename for all paths
        # Format: host.txt
        filename = f"{Config.SSH_HOST}.txt"
        output_file = Config.SNAPSHOT_DIR / filename
        
        # 2. Build SSH command with ALL paths
        # Result: find /app/data/continuite /app/amazon/continuite -type f
        remote_paths_str = " ".join(Config.REMOTE_PATHS)
        remote_cmd = f"find {remote_paths_str} -type f"
        
        ssh_cmd = [
            "ssh",
            "-i", Config.SSH_KEY_PATH,
            "-o", "BatchMode=yes", 
            "-o", "StrictHostKeyChecking=no",
            f"{Config.SSH_USER}@{Config.SSH_HOST}",
            remote_cmd
        ]

        log.info(f"Scanning remote paths: {remote_paths_str}")
        log.info(f"Saving to: {output_file}")
        
        try:
            with open(output_file, "w") as f_out:
                subprocess.run(ssh_cmd, stdout=f_out, stderr=subprocess.PIPE, check=True, text=True)
            
            if output_file.stat().st_size == 0:
                log.warning(f"File {filename} is empty. No files found in remote paths?")
            
            # Return list for compatibility with main.py
            return [output_file]
            
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to scan remote paths. Exit code: {e.returncode}")
            if e.stderr:
                log.error(f"Stderr: {e.stderr}")
            raise
