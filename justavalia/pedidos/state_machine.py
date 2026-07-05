"""Máquina de estados do Pedido.

Implementação própria (enum + tabela de transições permitidas), conforme CLAUDE.md:
não usar lib de FSM. Esta camada é *pura* (sem banco) — só decide o que é permitido.
A gravação de estado e o log imutável de transição ficam no modelo (models.py), que
também aplica o guard humano da transição APPROVED_FOR_SIGNATURE → SIGNED.

Regras invioláveis (CLAUDE.md > Máquina de estados):
- Transições proibidas devem falhar.
- Todo estado *pré-SIGNED* pode ir para CANCELLED; SIGNED e DELIVERED, não.
"""

from django.db import models


class PedidoStatus(models.TextChoices):
    DRAFT = "DRAFT", "Rascunho"
    AWAITING_PAYMENT = "AWAITING_PAYMENT", "Aguardando pagamento"
    AWAITING_UPLOAD = "AWAITING_UPLOAD", "Aguardando envio"
    PROCESSING = "PROCESSING", "Processando"
    PENDENCY = "PENDENCY", "Pendência"
    IN_TRIAGE = "IN_TRIAGE", "Em triagem"
    DRAFTING = "DRAFTING", "Gerando rascunho"
    IN_REVIEW = "IN_REVIEW", "Em revisão"
    APPROVED_FOR_SIGNATURE = "APPROVED_FOR_SIGNATURE", "Aprovado para assinatura"
    SIGNED = "SIGNED", "Assinado"
    DELIVERED = "DELIVERED", "Entregue"
    CANCELLED = "CANCELLED", "Cancelado"


S = PedidoStatus

# Transições do diagrama do CLAUDE.md (sem o CANCELLED, adicionado programaticamente).
_TRANSICOES_BASE: dict[str, set[str]] = {
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

# Estados pré-SIGNED (tudo que ainda não foi assinado, entregue ou cancelado).
ESTADOS_TERMINAIS: frozenset[str] = frozenset({S.SIGNED, S.DELIVERED, S.CANCELLED})
ESTADOS_PRE_SIGNED: frozenset[str] = frozenset(
    e for e in S.values if e not in {S.SIGNED, S.DELIVERED, S.CANCELLED}
)

# Tabela final: adiciona CANCELLED como alvo de todo estado pré-SIGNED.
TRANSICOES: dict[str, frozenset[str]] = {
    estado: frozenset(alvos | ({S.CANCELLED} if estado in ESTADOS_PRE_SIGNED else set()))
    for estado, alvos in _TRANSICOES_BASE.items()
}


class TransicaoInvalida(Exception):
    """Levantada quando se tenta uma transição de estado não permitida."""


def transicoes_permitidas(de: str) -> set[str]:
    """Conjunto de estados alcançáveis a partir de `de` (inclui CANCELLED se pré-SIGNED)."""
    return set(TRANSICOES[de])


def pode_transicionar(de: str, para: str) -> bool:
    return para in TRANSICOES[de]


def validar_transicao(de: str, para: str) -> None:
    """Levanta TransicaoInvalida se a transição não for permitida."""
    if not pode_transicionar(de, para):
        raise TransicaoInvalida(
            f"Transição proibida: {de} → {para}. "
            f"Permitidas de {de}: {sorted(TRANSICOES[de]) or '(nenhuma — estado terminal)'}."
        )
