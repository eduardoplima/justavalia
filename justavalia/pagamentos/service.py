"""Serviço de pagamento: seleciona o provedor por env var e orquestra as
transições de estado do Pedido em torno do pagamento.

CLAUDE.md: adapter com MockPix em dev e interface documentada para o provedor real.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction

from justavalia.pagamentos.base import PixProvider
from justavalia.pagamentos.mock import MockPix
from justavalia.pagamentos.models import Pagamento
from justavalia.pedidos.models import Pedido
from justavalia.pedidos.state_machine import PedidoStatus

# Registro de provedores disponíveis. Provedores reais (Mercado Pago, Efí) entram
# aqui quando implementados; a seleção continua por PIX_PROVIDER.
_PROVIDERS: dict[str, type[PixProvider]] = {
    "mock": MockPix,
}


def get_pix_provider() -> PixProvider:
    nome = getattr(settings, "PIX_PROVIDER", "mock")
    # Salvaguarda: MockPix aprova qualquer pagamento — jamais em produção.
    # prod.py força ALLOW_MOCK_PAYMENTS=False; dev/test deixam True.
    if nome == "mock" and not getattr(settings, "ALLOW_MOCK_PAYMENTS", True):
        raise ImproperlyConfigured(
            "PIX_PROVIDER='mock' com ALLOW_MOCK_PAYMENTS desligado (produção). O MockPix "
            "nunca deve rodar em produção; configure um provedor real."
        )
    try:
        return _PROVIDERS[nome]()
    except KeyError as exc:
        raise ImproperlyConfigured(
            f"PIX_PROVIDER='{nome}' desconhecido. Disponíveis: {sorted(_PROVIDERS)}."
        ) from exc


@transaction.atomic
def iniciar_pagamento(pedido: Pedido) -> Pagamento:
    """Cria a cobrança e move o pedido para AWAITING_PAYMENT (se ainda em DRAFT)."""
    provider = get_pix_provider()
    cob = provider.criar_cobranca(valor_centavos=pedido.preco_centavos, referencia=pedido.numero)
    pagamento = Pagamento.objects.create(
        pedido=pedido,
        provedor=cob.provedor,
        txid=cob.txid,
        valor_centavos=cob.valor_centavos,
        copia_e_cola=cob.copia_e_cola,
    )
    if pedido.status == PedidoStatus.DRAFT:
        pedido.transicionar(
            PedidoStatus.AWAITING_PAYMENT,
            ator_desc=f"pagamento:{cob.provedor}",
            motivo="cobrança PIX criada",
            payload={"txid": cob.txid},
        )
    return pagamento


@transaction.atomic
def confirmar_pagamento(pagamento: Pagamento) -> None:
    """Consulta o provedor; se aprovado, marca e move o pedido para AWAITING_UPLOAD."""
    provider = get_pix_provider()
    if provider.consultar(pagamento.txid) != "aprovado":
        return
    pagamento.status = Pagamento.Status.APROVADO
    pagamento.save(update_fields=["status", "atualizado_em"])
    pedido = pagamento.pedido
    if pedido.status == PedidoStatus.AWAITING_PAYMENT:
        pedido.transicionar(
            PedidoStatus.AWAITING_UPLOAD,
            ator_desc=f"pagamento:{pagamento.provedor}",
            motivo="pagamento aprovado",
            payload={"txid": pagamento.txid},
        )
