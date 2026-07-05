from django.apps import AppConfig


class TriagemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.triagem"
    label = "triagem"
    verbose_name = "triagem: score de risco fast_lane/deep_lane"
