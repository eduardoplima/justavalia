from django.apps import AppConfig


class SitePublicoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.site_publico"
    label = "site_publico"
    verbose_name = "site_publico: paginas publicas (identidade visual)"
