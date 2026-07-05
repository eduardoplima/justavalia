"""Adapter de pagamento PIX (MockPix) + serviço de início/confirmação.

Toda integração externa fica atrás de interface + mock trocável por env var
(CLAUDE.md). Em dev, PIX_PROVIDER=mock e a aprovação é simulada.
"""

import pytest
from django.test import override_settings

from justavalia.pagamentos.base import Cobranca, PixProvider
from justavalia.pagamentos.mock import MockPix
from justavalia.pagamentos.models import Pagamento
from justavalia.pagamentos.service import (
    confirmar_pagamento,
    get_pix_provider,
    iniciar_pagamento,
)
from justavalia.pedidos.models import Pedido
from justavalia.pedidos.state_machine import PedidoStatus as St

pytestmark = pytest.mark.django_db


def _pedido():
    return Pedido.objects.create(
        cliente_nome="Fulano", cliente_email="f@example.com", endereco_imovel="Rua X, 1"
    )


def test_mockpix_e_um_pixprovider():
    assert isinstance(MockPix(), PixProvider)


def test_mockpix_cria_cobranca_pendente():
    cob = MockPix().criar_cobranca(valor_centavos=29900, referencia="JV-TESTE")
    assert isinstance(cob, Cobranca)
    assert cob.status == "pendente"
    assert cob.valor_centavos == 29900
    assert cob.txid
    assert cob.copia_e_cola  # payload pix simulado


@override_settings(PIX_PROVIDER="mock")
def test_factory_retorna_mockpix():
    assert isinstance(get_pix_provider(), MockPix)


@override_settings(PIX_PROVIDER="inexistente")
def test_factory_falha_com_provedor_desconhecido():
    with pytest.raises(Exception):  # noqa: B017
        get_pix_provider()


@override_settings(PIX_PROVIDER="mock", ALLOW_MOCK_PAYMENTS=False)
def test_mockpix_bloqueado_em_producao():
    # MockPix aprova qualquer pagamento — jamais pode resolver quando mock é proibido.
    with pytest.raises(Exception):  # noqa: B017 - ImproperlyConfigured
        get_pix_provider()


@override_settings(PIX_PROVIDER="mock")
def test_iniciar_pagamento_cria_cobranca_e_move_para_awaiting_payment():
    p = _pedido()
    pag = iniciar_pagamento(p)
    p.refresh_from_db()
    assert isinstance(pag, Pagamento)
    assert pag.status == Pagamento.Status.PENDENTE
    assert p.status == St.AWAITING_PAYMENT
    # transição auditada
    assert p.transicoes.filter(para_status=St.AWAITING_PAYMENT).exists()


@override_settings(PIX_PROVIDER="mock")
def test_confirmar_pagamento_aprova_e_move_para_awaiting_upload():
    p = _pedido()
    pag = iniciar_pagamento(p)
    confirmar_pagamento(pag)
    p.refresh_from_db()
    pag.refresh_from_db()
    assert pag.status == Pagamento.Status.APROVADO
    assert p.status == St.AWAITING_UPLOAD
    # a transição do pagamento é atribuída ao provedor no log
    log = p.transicoes.get(para_status=St.AWAITING_UPLOAD)
    assert "mock" in log.ator_desc.lower()
