"""Views das páginas públicas.

`styleguide` é uma página interna de desenvolvimento: renderiza todos os tokens e
componentes da identidade visual para conferência visual. Fica atrás do flag
SHOW_STYLEGUIDE (ligado por padrão em dev, desligado em produção).
"""

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render


def styleguide(request: HttpRequest) -> HttpResponse:
    if not settings.SHOW_STYLEGUIDE:
        raise Http404
    return render(request, "styleguide.html")
