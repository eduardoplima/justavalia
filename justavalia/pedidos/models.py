"""Modelo Pedido e log imutável de transições.

A lógica de *quais* transições são permitidas vive em `state_machine.py`. Aqui
aplicamos: gravação atômica do estado + log de auditoria, e o guard humano da
transição para SIGNED (regra inviolável do CLAUDE.md).
"""

from __future__ import annotations

import secrets

from django.conf import settings
from django.db import models, transaction

from justavalia.pedidos.state_machine import (
    PedidoStatus,
    TransicaoInvalida,
    validar_transicao,
)


def _gerar_numero() -> str:
    return "JV-" + secrets.token_hex(4).upper()


class Pedido(models.Model):
    """Um pedido de avaliação. `status` é dirigido pela máquina de estados."""

    numero = models.CharField(max_length=20, unique=True, default=_gerar_numero, editable=False)
    status = models.CharField(
        max_length=32, choices=PedidoStatus.choices, default=PedidoStatus.DRAFT
    )

    # Dados mínimos (LGPD: só o necessário). Mais campos chegam nas fases seguintes.
    cliente_nome = models.CharField(max_length=160)
    cliente_email = models.EmailField()
    cliente_whatsapp = models.CharField(max_length=32, blank=True)
    endereco_imovel = models.CharField(max_length=255)
    tipo_imovel = models.CharField(max_length=40, default="residencial_urbano")
    preco_centavos = models.PositiveIntegerField(default=29900)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self) -> str:
        return f"{self.numero} ({self.get_status_display()})"

    @transaction.atomic
    def transicionar(
        self,
        novo_status: str,
        *,
        ator=None,
        por_humano: bool = False,
        motivo: str = "",
        payload: dict | None = None,
        ator_desc: str | None = None,
    ) -> TransicaoLog:
        """Executa uma transição de estado válida e grava o log de auditoria.

        - Recusa transições proibidas (TransicaoInvalida).
        - Recusa SIGNED que não venha de ação humana autenticada (nunca task/cron/
          webhook/IA): exige `ator` sendo um usuário persistido e `por_humano=True`.
        - Atômica: ou muda o estado E grava o log, ou nada.
        - Serializada: trava a linha do pedido (select_for_update) e revalida sob o lock,
          evitando dupla transição concorrente (ex.: dupla assinatura).
        """
        if self.pk is not None:
            atual = (
                Pedido.objects.select_for_update().values_list("status", flat=True).get(pk=self.pk)
            )
            self.status = atual  # estado autoritativo sob o lock

        validar_transicao(self.status, novo_status)

        if novo_status == PedidoStatus.SIGNED and not self._assinatura_autorizada(ator, por_humano):
            raise TransicaoInvalida(
                "APPROVED_FOR_SIGNATURE → SIGNED exige ação humana autenticada do "
                "avaliador (ator + por_humano=True). Nunca por task, cron, webhook ou IA."
            )

        de = self.status
        self.status = novo_status
        self.save(update_fields=["status", "atualizado_em"])

        return TransicaoLog.objects.create(
            pedido=self,
            de_status=de,
            para_status=novo_status,
            ator=ator if getattr(ator, "pk", None) else None,
            ator_desc=(ator_desc or (str(ator) if ator is not None else "sistema")),
            motivo=motivo,
            payload=payload or {},
        )

    @staticmethod
    def _assinatura_autorizada(ator, por_humano: bool) -> bool:
        # Precisa de um usuário persistido E do sinal explícito de ação humana.
        return bool(por_humano and ator is not None and getattr(ator, "pk", None))

    def timeline(self):
        """Transições em ordem cronológica (para a página de status/auditoria)."""
        return self.transicoes.all()


class ImmutableLogError(Exception):
    """Levantada ao tentar alterar/apagar um log de transição (append-only)."""


class TransicaoLog(models.Model):
    """Registro imutável de uma transição de estado (ator, timestamp, payload)."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="transicoes")
    de_status = models.CharField(max_length=32, choices=PedidoStatus.choices)
    para_status = models.CharField(max_length=32, choices=PedidoStatus.choices)
    ator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transicoes_pedido",
    )
    ator_desc = models.CharField(max_length=160, default="sistema")
    motivo = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em", "id"]
        verbose_name = "transição"
        verbose_name_plural = "transições"

    def __str__(self) -> str:
        return f"{self.pedido_id}: {self.de_status} → {self.para_status}"

    def save(self, *args, **kwargs):
        # Append-only: permite apenas a criação inicial.
        if not self._state.adding:
            raise ImmutableLogError("TransicaoLog é imutável (append-only).")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ImmutableLogError("TransicaoLog não pode ser apagado (trilha de auditoria).")
