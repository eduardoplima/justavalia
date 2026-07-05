"""Tasks utilitárias do core (smoke test do wiring do Celery)."""

from celery import shared_task


@shared_task(name="core.ping")
def ping() -> str:
    """Task trivial usada para provar que o Celery está corretamente conectado."""
    return "pong"
