from django.apps import AppConfig


class AssinaturaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.assinatura"
    label = "assinatura"
    verbose_name = "assinatura: adapter ICP (MockSigner em dev) e auditoria"
