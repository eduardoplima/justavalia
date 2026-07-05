#!/usr/bin/env python
"""Utilitário de linha de comando do Django para tarefas administrativas."""

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "justavalia.core.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Não foi possível importar o Django. Ele está instalado e disponível na "
            "PYTHONPATH? Você ativou o ambiente virtual (uv sync)?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
