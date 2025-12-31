import subprocess
import time
from pathlib import Path
from typing import List
from .log import get_logger
from .config import Config

log = get_logger()

class RemoteScanner:
    def generate_snapshots(self) -> List[Path]:
        """
        Runs ssh command for each configured path separately.
        Returns a list of local file paths containing the snapshots.
        """
        Config.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        
        generated_files = []

        for remote_path in Config.REMOTE_PATHS:
            # 1. Sanitize path for filename ( /app/data -> app_data )
            safe_path_name = remote_path.strip("/").replace("/", "_")
            
            # 2. Construct filename: timestamp-path-host.txt
            filename = f"{Config.SSH_HOST}-{safe_path_name}.txt"
            output_file = Config.SNAPSHOT_DIR / filename
            
            # 3. Build SSH command for this specific path
            # find /app/data/continuite -type f
            remote_cmd = f"find {remote_path} -type f"
            
            ssh_cmd = [
                "ssh",
                "-i", Config.SSH_KEY_PATH,
                "-o", "BatchMode=yes", 
                "-o", "StrictHostKeyChecking=no",
                f"{Config.SSH_USER}@{Config.SSH_HOST}",
                remote_cmd
            ]

            log.info(f"Scanning remote path: {remote_path}")
            log.info(f"Saving to: {output_file}")
            
            try:
                with open(output_file, "w") as f_out:
                    subprocess.run(ssh_cmd, stdout=f_out, stderr=subprocess.PIPE, check=True, text=True)
                
                if output_file.stat().st_size == 0:
                    log.warning(f"File {filename} is empty. No files found in {remote_path}?")
                
                generated_files.append(output_file)
                
            except subprocess.CalledProcessError as e:
                log.error(f"Failed to scan {remote_path}. Exit code: {e.returncode}")
                if e.stderr:
                    log.error(f"Stderr: {e.stderr}")
                # We raise here to stop execution, or you could 'continue' to try the next path
                raise

        return generated_files
