"""Settings de desenvolvimento (compose local)."""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True

# Permissivo em dev; ainda respeita DJANGO_ALLOWED_HOSTS se definido.
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "web", "*"])

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Execução ansiosa desligada em dev: as tasks passam pelo broker/worker de verdade.
CELERY_TASK_ALWAYS_EAGER = False
