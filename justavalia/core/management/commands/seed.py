from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Popula dados de exemplo (stub na Fase 0; dados reais chegam na Fase 3)."

    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.WARNING("seed: sem dados de exemplo ainda (chega na Fase 3)."))
