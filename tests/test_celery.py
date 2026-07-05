"""Wiring do Celery: com execução ansiosa (settings.test), a task ping roda inline.

Prova que o app Celery importa, a autodiscovery acha core.tasks e `-A justavalia`
resolve o mesmo objeto que o worker usa.
"""

from justavalia import celery_app
from justavalia.core.tasks import ping


def test_celery_app_nomeado():
    assert celery_app.main == "justavalia"


def test_ping_task_eager():
    result = ping.delay()
    assert result.get() == "pong"
