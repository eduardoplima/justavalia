"""Smoke das páginas públicas: rotas resolvem, nav ativa, um só <h1>."""

import pytest
from django.urls import reverse

PAGINAS = [
    "site_publico:home",
    "site_publico:como_funciona",
    "site_publico:advogados",
    "site_publico:quem_assina",
    "site_publico:faq",
    "site_publico:privacidade",
    "site_publico:termos",
]


@pytest.mark.parametrize("nome", PAGINAS)
def test_pagina_responde_200(client, nome):
    resp = client.get(reverse(nome))
    assert resp.status_code == 200


@pytest.mark.parametrize("nome", PAGINAS)
def test_pagina_tem_um_unico_h1(client, nome):
    html = client.get(reverse(nome)).content.decode()
    assert html.count("<h1") == 1, f"{nome} deveria ter exatamente um <h1>"


def test_home_marca_link_ativo_no_header(client):
    html = client.get(reverse("site_publico:home")).content.decode()
    assert 'aria-current="page"' in html


def test_paginas_incluem_header_e_footer(client):
    html = client.get(reverse("site_publico:faq")).content.decode()
    assert 'aria-label="Principal"' in html  # header
    assert "VALIDADOR OFICIAL DO ITI" in html  # footer
