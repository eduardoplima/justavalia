"""Pacote raiz do projeto Justavalia.

Expõe o app Celery na raiz do pacote para que `celery -A justavalia` resolva o
mesmo objeto usado por worker e beat.
"""

from justavalia.core.celery import app as celery_app

__all__ = ("celery_app",)
