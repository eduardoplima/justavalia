from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Renderiza o styleguide interno (stub na Fase 0; chega na Fase 1)."

    def handle(self, *args, **options) -> None:
        self.stdout.write(self.style.WARNING("styleguide: chega na Fase 1 (identidade -> tema)."))
