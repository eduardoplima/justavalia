"""Serviço de upload multipart presigned.

Implementa as 5 operações que o `@uppy/aws-s3` chama quando o backend é próprio
(sem Companion): create / signPart / listParts / complete / abort.

Segurança: toda operação que recebe (key, uploadId) valida que existe um MidiaAsset
daquele pedido criado por `criar_multipart` — nunca assinamos chaves arbitrárias.
"""

from __future__ import annotations

import uuid

from django.utils import timezone

from justavalia.pedidos.state_machine import PedidoStatus
from justavalia.uploads import s3
from justavalia.uploads.models import CategoriaMidia, MidiaAsset, StatusMidia

EXPIRACAO_SEG = 3600

# Estados em que o cliente pode enviar mídia (evita upload em SIGNED/DELIVERED/etc.).
ESTADOS_UPLOAD = frozenset({PedidoStatus.AWAITING_UPLOAD, PedidoStatus.PENDENCY})


class UploadNaoPermitido(Exception):
    """Upload tentado em um pedido cujo estado não aceita mídia."""


def _key(pedido, categoria: str, filename: str) -> str:
    safe = (filename or "arquivo").replace("/", "_").replace("\\", "_")[:120]
    return f"pedidos/{pedido.numero}/{categoria}/{uuid.uuid4().hex}-{safe}"


def _asset(pedido, upload_id: str, key: str) -> MidiaAsset:
    """Recupera o MidiaAsset que escopa esta chave a este pedido (ou 404)."""
    return MidiaAsset.objects.get(pedido=pedido, upload_id=upload_id, s3_key=key)


def criar_multipart(pedido, categoria: str, filename: str, content_type: str) -> dict:
    if pedido.status not in ESTADOS_UPLOAD:
        raise UploadNaoPermitido(f"Pedido em {pedido.status} não aceita upload de mídia.")
    if categoria not in CategoriaMidia.values:
        raise ValueError(f"Categoria inválida: {categoria}")
    client = s3.s3_client()
    key = _key(pedido, categoria, filename)
    resp = client.create_multipart_upload(
        Bucket=s3.bucket(),
        Key=key,
        ContentType=content_type or "application/octet-stream",
    )
    MidiaAsset.objects.create(
        pedido=pedido,
        categoria=categoria,
        s3_key=key,
        nome_original=filename or "",
        content_type=content_type or "",
        upload_id=resp["UploadId"],
        status=StatusMidia.EM_ANDAMENTO,
    )
    return {"uploadId": resp["UploadId"], "key": key}


def assinar_parte(pedido, upload_id: str, key: str, part_number: int) -> dict:
    _asset(pedido, upload_id, key)  # valida escopo
    # Presign com o endpoint público (a URL vai para o navegador).
    client = s3.s3_client(public=True)
    url = client.generate_presigned_url(
        "upload_part",
        Params={
            "Bucket": s3.bucket(),
            "Key": key,
            "UploadId": upload_id,
            "PartNumber": part_number,
        },
        ExpiresIn=EXPIRACAO_SEG,
        HttpMethod="PUT",
    )
    return {"url": url}


def listar_partes(pedido, upload_id: str, key: str) -> list[dict]:
    _asset(pedido, upload_id, key)
    client = s3.s3_client()
    resp = client.list_parts(Bucket=s3.bucket(), Key=key, UploadId=upload_id)
    return [
        {"PartNumber": p["PartNumber"], "Size": p["Size"], "ETag": p["ETag"]}
        for p in resp.get("Parts", [])
    ]


def completar(pedido, upload_id: str, key: str, parts: list[dict]) -> dict:
    asset = _asset(pedido, upload_id, key)
    client = s3.s3_client()
    ordenadas = sorted(parts, key=lambda p: int(p["PartNumber"]))
    resp = client.complete_multipart_upload(
        Bucket=s3.bucket(),
        Key=key,
        UploadId=upload_id,
        MultipartUpload={
            "Parts": [{"ETag": p["ETag"], "PartNumber": int(p["PartNumber"])} for p in ordenadas]
        },
    )
    head = client.head_object(Bucket=s3.bucket(), Key=key)
    asset.etag = (resp.get("ETag") or "").strip('"')
    asset.sha256 = head.get("ChecksumSHA256", "") or ""
    asset.tamanho_bytes = head.get("ContentLength", 0)
    asset.status = StatusMidia.RECEBIDO
    asset.recebido_em = timezone.now()
    asset.save(update_fields=["etag", "sha256", "tamanho_bytes", "status", "recebido_em"])
    return {"location": resp.get("Location", "")}


def abortar(pedido, upload_id: str, key: str) -> None:
    asset = _asset(pedido, upload_id, key)
    client = s3.s3_client()
    client.abort_multipart_upload(Bucket=s3.bucket(), Key=key, UploadId=upload_id)
    asset.delete()
