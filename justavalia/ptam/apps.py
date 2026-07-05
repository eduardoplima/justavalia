from django.apps import AppConfig


class PtamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.ptam"
    label = "ptam"
    verbose_name = "ptam: template do parecer, rascunho e render PDF"
