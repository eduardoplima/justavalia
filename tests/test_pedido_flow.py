"""Fluxo público de criação de pedido → pagamento (mock) → aguardando envio.

Aceite da Fase 3: pedido navega DRAFT → AWAITING_UPLOAD via mock, com timeline auditada.
"""

import pytest
from django.urls import reverse

from justavalia.pedidos.models import Pedido
from justavalia.pedidos.state_machine import PedidoStatus as St

# PIX_PROVIDER já é "mock" por padrão no ambiente de teste.
pytestmark = pytest.mark.django_db

DADOS = {
    "cliente_nome": "Fulano de Tal",
    "cliente_email": "fulano@example.com",
    "cliente_whatsapp": "11999999999",
    "endereco_imovel": "Rua das Flores, 100, São Paulo",
}


def test_criar_pedido_move_para_awaiting_payment(client):
    resp = client.post(reverse("pedidos:novo"), DADOS)
    p = Pedido.objects.get()
    assert p.status == St.AWAITING_PAYMENT
    assert resp.status_code == 302
    assert p.numero in resp.url  # redireciona para a página de pagamento


def test_form_invalido_nao_cria_pedido(client):
    resp = client.post(reverse("pedidos:novo"), {"cliente_nome": ""})
    assert resp.status_code == 200  # re-renderiza com erros
    assert Pedido.objects.count() == 0


def test_fluxo_completo_ate_awaiting_upload_com_timeline_auditada(client):
    # 1) cria o pedido
    client.post(reverse("pedidos:novo"), DADOS)
    p = Pedido.objects.get()
    assert p.status == St.AWAITING_PAYMENT

    # 2) simula o pagamento (MockPix aprova)
    resp = client.post(reverse("pedidos:pagamento", args=[p.numero]))
    assert resp.status_code == 302
    p.refresh_from_db()
    assert p.status == St.AWAITING_UPLOAD

    # 3) timeline auditada: DRAFT→AWAITING_PAYMENT→AWAITING_UPLOAD, com ator/timestamp
    estados = [(t.de_status, t.para_status) for t in p.timeline()]
    assert estados == [
        (St.DRAFT, St.AWAITING_PAYMENT),
        (St.AWAITING_PAYMENT, St.AWAITING_UPLOAD),
    ]
    for t in p.timeline():
        assert t.criado_em is not None
        assert t.ator_desc  # quem/que causou a transição


def test_pagina_de_status_mostra_timeline(client):
    client.post(reverse("pedidos:novo"), DADOS)
    p = Pedido.objects.get()
    resp = client.get(reverse("pedidos:status", args=[p.numero]))
    assert resp.status_code == 200
    assert p.numero in resp.content.decode()
