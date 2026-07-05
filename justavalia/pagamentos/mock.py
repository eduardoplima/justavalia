"""MockPix — provedor de PIX de desenvolvimento.

Não fala com nenhuma API. Gera um txid e um "copia e cola" fictícios e aprova a
cobrança quando consultado (simula pagamento). NUNCA usar em produção.
"""

from __future__ import annotations

import secrets

from justavalia.pagamentos.base import Cobranca, PixProvider


class MockPix(PixProvider):
    nome = "mock"

    def criar_cobranca(self, *, valor_centavos: int, referencia: str) -> Cobranca:
        txid = "MOCK-" + secrets.token_hex(8).upper()
        # "copia e cola" apenas ilustrativo (não é um BR Code válido).
        copia_e_cola = f"00020126MOCKPIX-{referencia}-{txid}5204000053039865802BR"
        return Cobranca(
            txid=txid,
            status="pendente",
            valor_centavos=valor_centavos,
            copia_e_cola=copia_e_cola,
            provedor=self.nome,
        )

    def consultar(self, txid: str) -> str:
        # Mock: toda cobrança consultada é considerada aprovada (pagamento simulado).
        return "aprovado"
