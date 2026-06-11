import sqlite3
import sys
import urllib.request
import json

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'db/alpha_vault.db'

# ── 1. Remove ERROR alphas from the local simulation queue ──────────────────
print("=" * 60)
print("STEP 1: Removing ERROR alphas from live queue via API")
print("=" * 60)

try:
    # Get current queue
    req = urllib.request.Request('http://localhost:8000/api/status')
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read().decode('utf-8', errors='replace'))

    alphas = data.get('alphas', [])
    error_formulas = [a['formula'] for a in alphas if a.get('status') == 'ERROR']
    good_alphas    = [a for a in alphas if a.get('status') != 'ERROR']

    print(f"  Total alphas in queue : {len(alphas)}")
    print(f"  ERROR alphas found    : {len(error_formulas)}")
    print(f"  Good alphas kept      : {len(good_alphas)}")

    if error_formulas:
        for i, f in enumerate(error_formulas, 1):
            print(f"  Removing [{i}]: {f[:80]}...")

        # Delete each ERROR alpha using the delete endpoint
        deleted = 0
        for alpha in alphas:
            if alpha.get('status') == 'ERROR':
                try:
                    del_data = json.dumps({'formula': alpha['formula']}).encode()
                    del_req  = urllib.request.Request(
                        'http://localhost:8000/api/delete-alpha',
                        data=del_data,
                        headers={'Content-Type': 'application/json'},
                        method='POST'
                    )
                    with urllib.request.urlopen(del_req, timeout=5) as dr:
                        deleted += 1
                except Exception as e:
                    print(f"  [WARN] Could not delete via API: {e}")
        print(f"  Deleted via API: {deleted}")
    else:
        print("  No ERROR alphas in queue — nothing to remove.")

except Exception as e:
    print(f"  [WARN] API check failed: {e}")

# ── 2. Clean ERROR records from the SQLite database ──────────────────────────
print()
print("=" * 60)
print("STEP 2: Cleaning ERROR records from alpha_vault.db")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# Find all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print(f"  Tables found: {tables}")

total_deleted = 0
for table in tables:
    try:
        # Check if table has a status column
        cur.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cur.fetchall()]
        if 'status' not in cols:
            continue

        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE status = 'ERROR'")
        error_count = cur.fetchone()[0]

        if error_count > 0:
            cur.execute(f"DELETE FROM {table} WHERE status = 'ERROR'")
            print(f"  [{table}] Deleted {error_count} ERROR records")
            total_deleted += error_count
        else:
            cur.execute(f"SELECT status, COUNT(*) FROM {table} GROUP BY status")
            rows = cur.fetchall()
            print(f"  [{table}] No ERRORs — statuses: {dict(rows)}")
    except Exception as e:
        print(f"  [{table}] Skip: {e}")

conn.commit()
conn.close()

print()
print("=" * 60)
print(f"TOTAL DB RECORDS DELETED : {total_deleted}")
print("=" * 60)

# ── 3. Verify API is now working without auth ────────────────────────────────
print()
print("=" * 60)
print("STEP 3: Verifying /api/alphas works without auth")
print("=" * 60)

try:
    with urllib.request.urlopen('http://localhost:8000/api/alphas', timeout=5) as r:
        body = json.loads(r.read().decode('utf-8', errors='replace'))
        print(f"  /api/alphas STATUS : {r.status} OK")
        print(f"  Alphas returned   : {len(body.get('alphas', []))}")
except urllib.error.HTTPError as e:
    print(f"  /api/alphas STATUS : {e.code} {e.reason} -- still broken!")
except Exception as e:
    print(f"  /api/alphas ERROR  : {e}")

# Check queue after cleanup
try:
    with urllib.request.urlopen('http://localhost:8000/api/status', timeout=5) as r:
        data = json.loads(r.read().decode('utf-8', errors='replace'))
        alphas = data.get('alphas', [])
        error_count = sum(1 for a in alphas if a.get('status') == 'ERROR')
        print(f"  /api/status queue : {len(alphas)} alphas, {error_count} ERRORs remaining")
except Exception as e:
    print(f"  /api/status ERROR  : {e}")

print()
print("ALL DONE")
