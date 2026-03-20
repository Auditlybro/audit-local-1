"""
Check LedgerX connections: Postgres, Redis, Backend health.
Run from repo root: python check_connections.py
"""
import os
import sys
from pathlib import Path

# Load .env from ledgerx/backend if present
env_path = Path(__file__).resolve().parent / "ledgerx" / "backend" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://ledgerx:ledgerx@localhost:5432/ledgerx")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

def check_postgres():
    try:
        import psycopg2
        from urllib.parse import urlparse
        u = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=u.hostname or "localhost",
            port=u.port or 5432,
            dbname=u.path.lstrip("/") or "ledgerx",
            user=u.username or "ledgerx",
            password=u.password or "",
            connect_timeout=3,
        )
        conn.close()
        return True, "OK"
    except ImportError:
        return None, "psycopg2 not installed (pip install psycopg2-binary)"
    except Exception as e:
        return False, str(e)

def check_redis():
    try:
        import redis
        r = redis.from_url(REDIS_URL, socket_connect_timeout=3)
        r.ping()
        return True, "OK"
    except ImportError:
        return None, "redis not installed (pip install redis)"
    except Exception as e:
        return False, str(e)

def check_backend():
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8000/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = resp.read().decode()
            return True, data or "OK"
    except Exception as e:
        return False, str(e)

def main():
    print("LedgerX connection check\n" + "-" * 40)
    ok = 0
    # Postgres
    status, msg = check_postgres()
    if status is True:
        print("Postgres:  OK")
        ok += 1
    elif status is False:
        print("Postgres:  FAIL -", msg)
    else:
        print("Postgres:  SKIP -", msg)
    # Redis
    status, msg = check_redis()
    if status is True:
        print("Redis:     OK")
        ok += 1
    elif status is False:
        print("Redis:     FAIL -", msg)
    else:
        print("Redis:     SKIP -", msg)
    # Backend
    status, msg = check_backend()
    if status is True:
        print("Backend:   OK", msg[:60] if msg else "")
        ok += 1
    else:
        print("Backend:   FAIL -", msg)
    print("-" * 40)
    print(f"Passed: {ok}/3")
    sys.exit(0 if ok >= 2 else 1)

if __name__ == "__main__":
    main()
