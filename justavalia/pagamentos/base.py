"""Interface do provedor de PIX. Implementações reais (Mercado Pago, Efí) e o
MockPix de dev seguem este contrato; a troca é por env var (PIX_PROVIDER).
"""

from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class Cobranca:
    """Resultado da criação de uma cobrança PIX."""

    txid: str
    status: str  # "pendente" | "aprovado" | "cancelado"
    valor_centavos: int
    copia_e_cola: str  # payload PIX "copia e cola" (BR Code)
    provedor: str


class PixProvider(abc.ABC):
    """Contrato mínimo de um provedor de cobrança PIX."""

    nome: str = "abstract"

    @abc.abstractmethod
    def criar_cobranca(self, *, valor_centavos: int, referencia: str) -> Cobranca:
        """Cria uma cobrança e devolve seus dados (txid, copia-e-cola, status)."""

    @abc.abstractmethod
    def consultar(self, txid: str) -> str:
        """Retorna o status atual da cobrança: 'pendente' | 'aprovado' | 'cancelado'."""
