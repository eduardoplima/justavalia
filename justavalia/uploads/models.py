"""Manifesto de mídia: cada arquivo enviado pelo protocolo guiado vira um MidiaAsset.

CLAUDE.md (pipeline, passo 1): tudo com hash e timestamp de recebimento. O upload em
si é resumível (multipart S3/MinIO via Uppy); aqui guardamos o registro e o estado.
"""

from __future__ import annotations

from django.db import models

from justavalia.pedidos.models import Pedido


class CategoriaMidia(models.TextChoices):
    # Roteiro guiado (README/design): fachada, ambientes, detalhes + vídeo-vistoria.
    FOTO_FACHADA = "foto_fachada", "Foto — fachada"
    FOTO_AMBIENTE = "foto_ambiente", "Foto — ambiente"
    FOTO_DETALHE = "foto_detalhe", "Foto — detalhe"
    VIDEO_VISTORIA = "video_vistoria", "Vídeo — vistoria"
    # Documentos.
    DOC_MATRICULA = "doc_matricula", "Documento — matrícula"
    DOC_IPTU = "doc_iptu", "Documento — IPTU"
    DOC_COMPLEMENTAR = "doc_complementar", "Documento — complementar"


# Itens obrigatórios do protocolo (checagem de completude). Habite-se/planta "ajudam,
# se tiver" — não bloqueiam (ver README > Como funciona).
CATEGORIAS_OBRIGATORIAS: tuple[str, ...] = (
    CategoriaMidia.FOTO_FACHADA,
    CategoriaMidia.VIDEO_VISTORIA,
    CategoriaMidia.DOC_MATRICULA,
    CategoriaMidia.DOC_IPTU,
)


class StatusMidia(models.TextChoices):
    EM_ANDAMENTO = "em_andamento", "Upload em andamento"
    RECEBIDO = "recebido", "Recebido"
    ERRO = "erro", "Erro"


class MidiaAsset(models.Model):
    """Um arquivo de mídia/documento associado a um pedido."""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="midias")
    categoria = models.CharField(max_length=24, choices=CategoriaMidia.choices)
    s3_key = models.CharField(max_length=512, unique=True)
    nome_original = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=120, blank=True)
    tamanho_bytes = models.BigIntegerField(default=0)

    # Integridade: ETag do multipart (hash de conteúdo do S3) e, quando disponível,
    # checksum SHA-256 do objeto. Ao menos um serve de âncora de integridade.
    etag = models.CharField(max_length=128, blank=True)
    sha256 = models.CharField(max_length=64, blank=True)

    # Estado do upload resumível.
    upload_id = models.CharField(max_length=255, blank=True)  # multipart UploadId
    status = models.CharField(
        max_length=16, choices=StatusMidia.choices, default=StatusMidia.EM_ANDAMENTO
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    recebido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["criado_em", "id"]
        verbose_name = "mídia"
        verbose_name_plural = "mídias"

    def __str__(self) -> str:
        return f"{self.pedido_id}/{self.categoria}: {self.nome_original or self.s3_key}"


def completude(pedido: Pedido) -> dict:
    """Avalia o manifesto do pedido contra o checklist obrigatório do protocolo.

    Retorna {'completo': bool, 'faltando': [categorias], 'recebidas': [categorias]}.
    """
    recebidas = set(
        pedido.midias.filter(status=StatusMidia.RECEBIDO).values_list("categoria", flat=True)
    )
    faltando = [c for c in CATEGORIAS_OBRIGATORIAS if c not in recebidas]
    return {
        "completo": not faltando,
        "faltando": faltando,
        "recebidas": sorted(recebidas),
    }
