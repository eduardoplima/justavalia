"""Modelo Pedido + log imutável de transição + guard humano do SIGNED (com banco).

CLAUDE.md, regras invioláveis da máquina de estados:
1. APPROVED_FOR_SIGNATURE → SIGNED só por ação humana autenticada (nunca task/cron/webhook/IA).
2. Toda transição registra ator, timestamp e payload no log de auditoria.
3. Transições proibidas falham.
"""

import pytest
from django.contrib.auth import get_user_model

from justavalia.pedidos.models import Pedido
from justavalia.pedidos.state_machine import PedidoStatus as St
from justavalia.pedidos.state_machine import TransicaoInvalida

pytestmark = pytest.mark.django_db

User = get_user_model()


def _avaliador():
    return User.objects.create_user(username="eduardo", password="x", is_staff=True)


def novo_pedido():
    return Pedido.objects.create(
        cliente_nome="Fulano",
        cliente_email="fulano@example.com",
        endereco_imovel="Rua X, 100",
    )


def avancar(pedido, *estados, ator=None):
    """Helper para levar o pedido por uma sequência de estados válidos."""
    for e in estados:
        pedido.transicionar(e, ator=ator, por_humano=(e == St.SIGNED))


def test_novo_pedido_comeca_em_draft():
    assert novo_pedido().status == St.DRAFT


def test_transicao_valida_atualiza_status_e_grava_log():
    p = novo_pedido()
    log = p.transicionar(St.AWAITING_PAYMENT, ator=None, motivo="criado")
    p.refresh_from_db()
    assert p.status == St.AWAITING_PAYMENT
    assert log.de_status == St.DRAFT
    assert log.para_status == St.AWAITING_PAYMENT
    assert log.criado_em is not None
    assert p.transicoes.count() == 1


def test_transicao_proibida_levanta_e_nao_altera_estado():
    p = novo_pedido()
    with pytest.raises(TransicaoInvalida):
        p.transicionar(St.SIGNED)  # DRAFT → SIGNED é proibido
    p.refresh_from_db()
    assert p.status == St.DRAFT
    assert p.transicoes.count() == 0  # atômico: nada gravado


def test_signed_por_humano_autenticado_funciona():
    p = novo_pedido()
    avaliador = _avaliador()
    avancar(
        p,
        St.AWAITING_PAYMENT,
        St.AWAITING_UPLOAD,
        St.PROCESSING,
        St.IN_TRIAGE,
        St.DRAFTING,
        St.IN_REVIEW,
        St.APPROVED_FOR_SIGNATURE,
    )
    p.transicionar(St.SIGNED, ator=avaliador, por_humano=True)
    p.refresh_from_db()
    assert p.status == St.SIGNED


def test_signed_sem_humano_e_proibido():
    p = novo_pedido()
    avancar(
        p,
        St.AWAITING_PAYMENT,
        St.AWAITING_UPLOAD,
        St.PROCESSING,
        St.IN_TRIAGE,
        St.DRAFTING,
        St.IN_REVIEW,
        St.APPROVED_FOR_SIGNATURE,
    )
    # Sem ator humano / por_humano=False → recusado (simula task/cron/webhook/IA).
    with pytest.raises(TransicaoInvalida):
        p.transicionar(St.SIGNED, ator=None, por_humano=False)
    with pytest.raises(TransicaoInvalida):
        p.transicionar(St.SIGNED, ator=None, por_humano=True)  # por_humano sem ator não basta
    p.refresh_from_db()
    assert p.status == St.APPROVED_FOR_SIGNATURE


def test_log_de_transicao_e_imutavel():
    p = novo_pedido()
    log = p.transicionar(St.AWAITING_PAYMENT)
    log.para_status = St.CANCELLED
    with pytest.raises(Exception):  # noqa: B017 - qualquer bloqueio de escrita serve
        log.save()


def test_cancelar_a_partir_de_estado_pre_signed():
    p = novo_pedido()
    p.transicionar(St.AWAITING_PAYMENT)
    p.transicionar(St.CANCELLED, motivo="desistência")
    p.refresh_from_db()
    assert p.status == St.CANCELLED


def test_timeline_ordenada_por_criacao():
    p = novo_pedido()
    p.transicionar(St.AWAITING_PAYMENT)
    p.transicionar(St.AWAITING_UPLOAD)
    estados = [t.para_status for t in p.timeline()]
    assert estados == [St.AWAITING_PAYMENT, St.AWAITING_UPLOAD]


def test_ator_e_registrado_no_log():
    p = novo_pedido()
    avaliador = _avaliador()
    log = p.transicionar(St.AWAITING_PAYMENT, ator=avaliador)
    assert log.ator == avaliador
    assert "eduardo" in log.ator_desc
