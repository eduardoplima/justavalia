"""Máquina de estados do Pedido — lógica pura (sem banco).

CLAUDE.md exige cobertura exaustiva: toda transição permitida funciona e TODA
transição não documentada falha. Estas são as regras invioláveis da FSM.
"""

import pytest

from justavalia.pedidos.state_machine import (
    PedidoStatus as S,
)
from justavalia.pedidos.state_machine import (
    TransicaoInvalida,
    pode_transicionar,
    transicoes_permitidas,
    validar_transicao,
)

# Fonte de verdade do teste — o diagrama do CLAUDE.md (sem o CANCELLED, adicionado à parte).
ESPERADO_BASE = {
    S.DRAFT: {S.AWAITING_PAYMENT},
    S.AWAITING_PAYMENT: {S.AWAITING_UPLOAD},
    S.AWAITING_UPLOAD: {S.PROCESSING},
    S.PROCESSING: {S.PENDENCY, S.IN_TRIAGE},
    S.PENDENCY: {S.AWAITING_UPLOAD},
    S.IN_TRIAGE: {S.DRAFTING},
    S.DRAFTING: {S.IN_REVIEW},
    S.IN_REVIEW: {S.PENDENCY, S.APPROVED_FOR_SIGNATURE},
    S.APPROVED_FOR_SIGNATURE: {S.SIGNED},
    S.SIGNED: {S.DELIVERED},
    S.DELIVERED: set(),
    S.CANCELLED: set(),
}
# Todo estado pré-SIGNED pode ser CANCELADO (SIGNED e DELIVERED não).
PRE_SIGNED = {
    S.DRAFT,
    S.AWAITING_PAYMENT,
    S.AWAITING_UPLOAD,
    S.PROCESSING,
    S.PENDENCY,
    S.IN_TRIAGE,
    S.DRAFTING,
    S.IN_REVIEW,
    S.APPROVED_FOR_SIGNATURE,
}


def esperado_com_cancel(estado):
    alvos = set(ESPERADO_BASE[estado])
    if estado in PRE_SIGNED:
        alvos.add(S.CANCELLED)
    return alvos


TODOS = list(S)


def test_tracer_transicao_valida():
    assert pode_transicionar(S.DRAFT, S.AWAITING_PAYMENT) is True


@pytest.mark.parametrize("estado", TODOS)
def test_transicoes_permitidas_batem_com_o_diagrama(estado):
    assert transicoes_permitidas(estado) == esperado_com_cancel(estado)


@pytest.mark.parametrize("de", TODOS)
@pytest.mark.parametrize("para", TODOS)
def test_exaustivo_permitido_vs_proibido(de, para):
    permitido = para in esperado_com_cancel(de)
    assert pode_transicionar(de, para) is permitido
    if permitido:
        validar_transicao(de, para)  # não levanta
    else:
        with pytest.raises(TransicaoInvalida):
            validar_transicao(de, para)


def test_estados_terminais_nao_saem():
    assert transicoes_permitidas(S.DELIVERED) == set()
    assert transicoes_permitidas(S.CANCELLED) == set()


def test_signed_e_delivered_nao_cancelam():
    assert not pode_transicionar(S.SIGNED, S.CANCELLED)
    assert not pode_transicionar(S.DELIVERED, S.CANCELLED)


def test_todo_pre_signed_cancela():
    for estado in PRE_SIGNED:
        assert pode_transicionar(estado, S.CANCELLED), estado
