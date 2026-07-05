"""Endpoints de upload multipart (contrato do @uppy/aws-s3) + protocolo guiado.

As rotas JSON espelham as 5 funções do plugin. CSRF é exigido nos POST/DELETE; o JS
da página envia o header X-CSRFToken. O escopo (pedido × key × uploadId) é validado
no serviço — nunca assinamos chaves arbitrárias.
"""

from __future__ import annotations

import json

from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from justavalia.pedidos.models import Pedido
from justavalia.pedidos.state_machine import PedidoStatus
from justavalia.uploads import service
from justavalia.uploads.models import (
    CATEGORIAS_OBRIGATORIAS,
    CategoriaMidia,
    MidiaAsset,
    completude,
)


def _pedido(numero: str) -> Pedido:
    return get_object_or_404(Pedido, numero=numero)


def _json(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


@require_http_methods(["POST"])
def s3_create(request, numero):
    pedido = _pedido(numero)
    data = _json(request)
    categoria = data.get("categoria") or ""
    filename = data.get("filename") or data.get("name") or ""
    content_type = data.get("type") or data.get("contentType") or ""
    try:
        return JsonResponse(service.criar_multipart(pedido, categoria, filename, content_type))
    except service.UploadNaoPermitido as exc:
        return JsonResponse({"erro": str(exc)}, status=409)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))


@require_http_methods(["GET"])
def s3_sign_part(request, numero, upload_id, part_number):
    pedido = _pedido(numero)
    key = request.GET.get("key")
    if not key:
        return HttpResponseBadRequest("key ausente")
    try:
        return JsonResponse(service.assinar_parte(pedido, upload_id, key, int(part_number)))
    except MidiaAsset.DoesNotExist as exc:
        raise Http404 from exc


@require_http_methods(["GET", "DELETE"])
def s3_upload(request, numero, upload_id):
    pedido = _pedido(numero)
    key = request.GET.get("key")
    if not key:
        return HttpResponseBadRequest("key ausente")
    try:
        if request.method == "DELETE":
            service.abortar(pedido, upload_id, key)
            return JsonResponse({})
        return JsonResponse(service.listar_partes(pedido, upload_id, key), safe=False)
    except MidiaAsset.DoesNotExist as exc:
        raise Http404 from exc


@require_http_methods(["POST"])
def s3_complete(request, numero, upload_id):
    pedido = _pedido(numero)
    key = request.GET.get("key")
    if not key:
        return HttpResponseBadRequest("key ausente")
    parts = _json(request).get("parts", [])
    try:
        return JsonResponse(service.completar(pedido, upload_id, key, parts))
    except MidiaAsset.DoesNotExist as exc:
        raise Http404 from exc


def enviar(request, numero):
    """Página do protocolo guiado: uploaders por categoria + estado de completude."""
    pedido = _pedido(numero)
    obrigatorias = set(CATEGORIAS_OBRIGATORIAS)
    categorias = [
        {
            "valor": c.value,
            "label": c.label,
            "obrigatoria": c.value in obrigatorias,
        }
        for c in CategoriaMidia
    ]
    return render(
        request,
        "uploads/enviar.html",
        {"pedido": pedido, "categorias": categorias, "completude": completude(pedido)},
    )


@require_http_methods(["POST"])
def concluir(request, numero):
    """Fecha o envio: se completo e em AWAITING_UPLOAD, avança para PROCESSING."""
    pedido = _pedido(numero)
    if completude(pedido)["completo"] and pedido.status == PedidoStatus.AWAITING_UPLOAD:
        pedido.transicionar(
            PedidoStatus.PROCESSING,
            ator_desc="cliente",
            motivo="envio de mídia concluído",
        )
    return redirect("pedidos:status", numero=pedido.numero)
