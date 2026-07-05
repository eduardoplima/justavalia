"""Settings de teste — rápido, isolado, sem broker.

Celery ansioso (as tasks rodam inline), hasher de senha rápido, e-mail em memória.
"""

from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Sem broker nos testes: tasks executam inline e propagam exceções.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
