from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy.engine.url import make_url

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import psycopg2  # noqa: E402
from psycopg2 import sql as psql  # noqa: E402
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT  # noqa: E402

from app.core.config import settings  # noqa: E402


def main() -> None:
    url = make_url(settings.DATABASE_URL)
    target = url.database
    if not target:
        raise SystemExit("DATABASE_URL must include a database name")

    conn = psycopg2.connect(
        host=url.host or "localhost",
        port=int(url.port) if url.port else 5432,
        user=url.username,
        password=url.password,
        dbname="postgres",
        connect_timeout=10,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (target,),
            )
            if cur.fetchone():
                print(f"Database {target!r} already exists.")
                return
            cur.execute(psql.SQL("CREATE DATABASE {}").format(psql.Identifier(target)))
            print(f"Created database {target!r}.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
