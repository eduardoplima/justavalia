"""Smoke do wiring de settings: Django sobe, os 11 apps registram, User customizado."""

from django.apps import apps
from django.conf import settings

EXPECTED_LOCAL_APPS = {
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
}


def test_todos_os_apps_locais_registrados():
    installed = set(settings.INSTALLED_APPS)
    assert EXPECTED_LOCAL_APPS <= installed


def test_apps_carregam_sem_erro():
    # Se algum apps.py tiver name/label errado, isto falha ao resolver.
    labels = {cfg.label for cfg in apps.get_app_configs()}
    for expected in ("core", "pedidos", "assinatura", "site_publico", "dashboard"):
        assert expected in labels


def test_user_model_customizado():
    assert settings.AUTH_USER_MODEL == "core.User"


def test_locale_e_timezone_brasil():
    assert settings.LANGUAGE_CODE == "pt-br"
    assert settings.TIME_ZONE == "America/Sao_Paulo"
    assert settings.USE_TZ is True
