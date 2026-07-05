"""Endpoints de saúde.

- /healthz/  : liveness — não toca o banco (usado pelo healthcheck do container).
- /readyz/   : readiness — verifica banco e Redis; 200 se pronto, 503 se não.
"""

from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def healthz(request) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def readyz(request) -> JsonResponse:
    checks: dict[str, str] = {}
    healthy = True

    # Banco
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["database"] = "ok"
    except OperationalError:
        checks["database"] = "erro"
        healthy = False

    # Redis (broker do Celery)
    try:
        import redis
        from django.conf import settings

        client = redis.Redis.from_url(settings.CELERY_BROKER_URL)
        client.ping()
        checks["redis"] = "ok"
    except Exception:  # noqa: BLE001 - readiness reporta indisponibilidade, não propaga
        checks["redis"] = "erro"
        healthy = False

    status_code = 200 if healthy else 503
    return JsonResponse(
        {"status": "ready" if healthy else "unready", "checks": checks},
        status=status_code,
    )
