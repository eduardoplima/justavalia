"""Modelo de acompanhamento de pagamento (independente do provedor)."""

from __future__ import annotations

from django.db import models

from justavalia.pedidos.models import Pedido


class Pagamento(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADO = "aprovado", "Aprovado"
        CANCELADO = "cancelado", "Cancelado"

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="pagamentos")
    provedor = models.CharField(max_length=40)
    txid = models.CharField(max_length=80, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDENTE)
    valor_centavos = models.PositiveIntegerField()
    copia_e_cola = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "pagamento"
        verbose_name_plural = "pagamentos"

    def __str__(self) -> str:
        return f"{self.txid} ({self.get_status_display()})"
