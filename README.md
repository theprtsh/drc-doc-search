# DB Asset Mapper

High-throughput asset mapper. Links MySQL records to filesystem paths via Local I/O or SSH with flexible Source/Destination database. Designed for idempotency and speed.

## Quick Start

### 1. Environment
```bash
cp .env.example .env
# Edit .env with 
# 1. MySQL credentials for source and destination table
# 2. SSH user/host if searching from remote
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
*   **`PATHS`**: List of absolute remote directories to index.

## Usage

1. If searching locally
```bash
uv run start
```
2. If searching from remote
```bash
uv run start-remote
```

## Logic

*   **Filename Matching**: Case-insensitive (`os.path.basename`).
*   **Multi-Path**: If a file exists in multiple remote locations, paths are joined by a comma.
*   **State**: Tracks `_exist` (0/1) and `_path` (varchar). Only processes records where `exist=0`.
