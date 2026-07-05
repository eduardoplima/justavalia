#!/usr/bin/env bash
# Entrypoint compartilhado. Só o serviço web aplica migrações (evita corrida
# entre web/worker/beat). Defina RUN_MIGRATIONS=1 no serviço web.
set -euo pipefail

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  echo "[entrypoint] aguardando o banco..."
  python - <<'PY'
import os
import time

import psycopg

url = os.environ.get("DATABASE_URL", "")
deadline = time.time() + 60
while True:
    try:
        psycopg.connect(url, connect_timeout=3).close()
        print("[entrypoint] banco disponível.")
        break
    except Exception as exc:  # noqa: BLE001
        if time.time() > deadline:
            raise SystemExit(f"[entrypoint] banco indisponível: {exc}")
        time.sleep(1)
PY
  echo "[entrypoint] aplicando migrações..."
  python manage.py migrate --noinput
fi

exec "$@"
