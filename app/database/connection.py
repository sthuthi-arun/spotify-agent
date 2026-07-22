from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "spotify.duckdb"


def get_connection() -> duckdb.DuckDBPyConnection:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}"
        )

    return duckdb.connect(
        database=str(DATABASE_PATH),
        read_only=True,
    )

