"""Settings base — compartilhado por dev/prod/test. Tudo sensível vem de env.

Ver justavalia/core/settings/{dev,prod,test}.py para os overrides por ambiente.
"""

from pathlib import Path

import environ

# BASE_DIR = raiz do repositório (…/justavalia/core/settings/base.py -> sobe 4 níveis).
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    AWS_S3_USE_SSL=(bool, False),
)

# Em dev, o .env é lido pelo compose (env_file). Se existir um .env local, também o lê.
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    env.read_env(str(_env_file))

# ---- Núcleo ----
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-trocar")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("DJANGO_CSRF_TRUSTED_ORIGINS")

# ---- Apps ----
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Monólito modular — os 11 apps do projeto (ver CLAUDE.md > Arquitetura).
LOCAL_APPS = [
    "justavalia.core",
    "justavalia.pedidos",
    "justavalia.pagamentos",
    "justavalia.uploads",
    "justavalia.pipeline",
    "justavalia.triagem",
    "justavalia.ptam",
    "justavalia.assinatura",
    "justavalia.notificacoes",
    "justavalia.site_publico",
    "justavalia.dashboard",
]

INSTALLED_APPS = [*DJANGO_APPS, *LOCAL_APPS]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "justavalia.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "justavalia.core.wsgi.application"
ASGI_APPLICATION = "justavalia.core.asgi.application"

# ---- Banco ----
DATABASES = {"default": env.db("DATABASE_URL")}

# ---- Auth ----
AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---- i18n / tz ----
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ---- Static / media ----
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [d for d in [BASE_DIR / "static"] if d.exists()]

# Armazenamento S3-compatível (MinIO em dev) via django-storages.
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": env("AWS_STORAGE_BUCKET_NAME", default="justavalia-media"),
            "endpoint_url": env("AWS_S3_ENDPOINT_URL", default=""),
            "region_name": env("AWS_S3_REGION_NAME", default="us-east-1"),
            "use_ssl": env("AWS_S3_USE_SSL"),
            "access_key": env("AWS_ACCESS_KEY_ID", default=""),
            "secret_key": env("AWS_SECRET_ACCESS_KEY", default=""),
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Celery ----
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")
CELERY_TASK_DEFAULT_QUEUE = "media"
CELERY_TASK_QUEUES_NAMES = ["media", "docs", "ia", "notify"]
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = TIME_ZONE

# ---- Adapters de provedores (mock em dev; trocáveis por env var) ----
PIX_PROVIDER = env("PIX_PROVIDER", default="mock")
SIGNER_PROVIDER = env("SIGNER_PROVIDER", default="mock")
NOTIFIER_PROVIDER = env("NOTIFIER_PROVIDER", default="console")

# ---- Anthropic (adiado; placeholder — nunca fixar string de modelo sem docs.claude.com) ----
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL", default="")
