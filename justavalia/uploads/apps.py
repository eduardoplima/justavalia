from django.apps import AppConfig


class UploadsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.uploads"
    label = "uploads"
    verbose_name = "uploads: presigned URLs, manifesto de midia, protocolo guiado"
