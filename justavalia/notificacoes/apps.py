from django.apps import AppConfig


class NotificacoesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.notificacoes"
    label = "notificacoes"
    verbose_name = "notificacoes: adapter WhatsApp/e-mail (ConsoleNotifier em dev)"
