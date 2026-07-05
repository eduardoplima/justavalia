from django.apps import AppConfig


class PagamentosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.pagamentos"
    label = "pagamentos"
    verbose_name = "pagamentos: adapter PIX (MockPix em dev)"
