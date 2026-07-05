from django.apps import AppConfig


class PipelineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.pipeline"
    label = "pipeline"
    verbose_name = "pipeline: tasks Celery de frames, extracao e analise"
