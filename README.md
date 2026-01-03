# DRC Documents Search

High-throughput synchronization engine connecting local MySQL metadata with remote filesystem paths via SSH. Designed for idempotency and speed.

## Quick Start

### 1. Environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials and SSH user/host
```

### 2. Auth
Place your private key in the project root. Ensure the filename matches `config.py` (default: `ssh.key`).
```bash
chmod 600 ssh.key
```

### 3. Dependencies
```bash
uv sync
```

## Configuration

Modify `src/drc_doc_search/config.py` to tweak:

*   **`TABLE_MAP`**: `{"source_table": "dest_table"}`
*   **`REMOTE_PATHS`**: List of absolute remote directories to index.

## Usage

```bash
uv run main
```

## Logic

*   **Filename Matching**: Case-insensitive (`os.path.basename`).
*   **Multi-Path**: If a file exists in multiple remote locations, paths are joined by a comma.
*   **State**: Tracks `_exist` (0/1) and `_path` (varchar). Only processes records where `exist=0`.
