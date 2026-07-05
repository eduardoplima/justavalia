"""App Celery do Justavalia.

Filas: media, docs, ia, notify (ver CLAUDE.md). O worker é iniciado com
`celery -A justavalia worker -Q media,docs,ia,notify`.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "justavalia.core.settings.dev")

app = Celery("justavalia")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:  # pragma: no cover - utilitário de diagnóstico
    print(f"Request: {self.request!r}")
