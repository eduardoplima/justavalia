"""Endpoints multipart (contrato @uppy/aws-s3) + conclusão do envio.

O cliente S3 é falsificado (sem MinIO real); validamos o contrato JSON, o escopo de
segurança (chave pertence ao pedido) e as transições de estado.
"""

import json

import pytest
from django.urls import reverse

from justavalia.pedidos.models import Pedido
from justavalia.pedidos.state_machine import PedidoStatus as St
from justavalia.uploads.models import (
    CATEGORIAS_OBRIGATORIAS,
    CategoriaMidia,
    MidiaAsset,
    StatusMidia,
)

pytestmark = pytest.mark.django_db


class FakeS3:
    def create_multipart_upload(self, Bucket, Key, ContentType=None):
        return {"UploadId": "UP-1"}

    def generate_presigned_url(self, ClientMethod, Params, ExpiresIn, HttpMethod):
        return f"http://minio:9000/{Params['Key']}?partNumber={Params['PartNumber']}"

    def list_parts(self, Bucket, Key, UploadId):
        return {"Parts": [{"PartNumber": 1, "Size": 5242880, "ETag": '"abc"'}]}

    def complete_multipart_upload(self, Bucket, Key, UploadId, MultipartUpload):
        return {"ETag": '"final-etag"', "Location": f"http://minio:9000/{Key}"}

    def head_object(self, Bucket, Key):
        return {"ContentLength": 123456, "ChecksumSHA256": ""}

    def abort_multipart_upload(self, Bucket, Key, UploadId):
        return {}


@pytest.fixture(autouse=True)
def _fake_s3(monkeypatch):
    monkeypatch.setattr("justavalia.uploads.s3.s3_client", lambda **kw: FakeS3())


def _pedido(status=St.AWAITING_UPLOAD):
    p = Pedido.objects.create(
        cliente_nome="F", cliente_email="f@example.com", endereco_imovel="R X, 1"
    )
    # leva ao estado desejado por transições válidas
    caminho = [St.AWAITING_PAYMENT, St.AWAITING_UPLOAD]
    for e in caminho:
        p.transicionar(e)
        if e == status:
            break
    return p


def _criar_upload(client, pedido, categoria=CategoriaMidia.VIDEO_VISTORIA):
    url = reverse("uploads:s3_create", args=[pedido.numero])
    resp = client.post(
        url,
        data=json.dumps({"filename": "vid.mp4", "type": "video/mp4", "categoria": categoria}),
        content_type="application/json",
    )
    return resp


def test_create_cria_asset_em_andamento(client):
    p = _pedido()
    resp = _criar_upload(client, p)
    assert resp.status_code == 200
    body = resp.json()
    assert body["uploadId"] == "UP-1"
    asset = MidiaAsset.objects.get()
    assert asset.status == StatusMidia.EM_ANDAMENTO
    assert asset.s3_key == body["key"]


def test_create_recusa_categoria_invalida(client):
    p = _pedido()
    resp = client.post(
        reverse("uploads:s3_create", args=[p.numero]),
        data=json.dumps({"filename": "x", "categoria": "inexistente"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert MidiaAsset.objects.count() == 0


def test_create_recusado_em_estado_sem_upload(client):
    # Pedido em DRAFT (sem pagamento) não aceita upload → 409.
    p = Pedido.objects.create(
        cliente_nome="F", cliente_email="f@example.com", endereco_imovel="R X, 1"
    )
    resp = _criar_upload(client, p)
    assert resp.status_code == 409
    assert MidiaAsset.objects.count() == 0


def test_sign_part_retorna_url_e_escopa_por_pedido(client):
    p = _pedido()
    key = _criar_upload(client, p).json()["key"]
    resp = client.get(reverse("uploads:s3_sign_part", args=[p.numero, "UP-1", 1]) + f"?key={key}")
    assert resp.status_code == 200
    assert "url" in resp.json()
    # chave inexistente (não pertence a nenhum asset) → 404 (não assina arbitrário)
    resp404 = client.get(
        reverse("uploads:s3_sign_part", args=[p.numero, "UP-1", 1]) + "?key=chave/arbitraria"
    )
    assert resp404.status_code == 404


def test_list_parts(client):
    p = _pedido()
    key = _criar_upload(client, p).json()["key"]
    resp = client.get(reverse("uploads:s3_upload", args=[p.numero, "UP-1"]) + f"?key={key}")
    assert resp.status_code == 200
    assert resp.json()[0]["PartNumber"] == 1


def test_complete_marca_recebido(client):
    p = _pedido()
    key = _criar_upload(client, p).json()["key"]
    url = reverse("uploads:s3_complete", args=[p.numero, "UP-1"]) + f"?key={key}"
    resp = client.post(
        url,
        data=json.dumps({"parts": [{"PartNumber": 1, "ETag": '"abc"'}]}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    asset = MidiaAsset.objects.get()
    assert asset.status == StatusMidia.RECEBIDO
    assert asset.etag == "final-etag"
    assert asset.tamanho_bytes == 123456
    assert asset.recebido_em is not None


def test_abort_remove_asset(client):
    p = _pedido()
    key = _criar_upload(client, p).json()["key"]
    resp = client.delete(reverse("uploads:s3_upload", args=[p.numero, "UP-1"]) + f"?key={key}")
    assert resp.status_code == 200
    assert MidiaAsset.objects.count() == 0


def test_concluir_incompleto_nao_avanca(client):
    p = _pedido()
    resp = client.post(reverse("uploads:concluir", args=[p.numero]))
    p.refresh_from_db()
    assert resp.status_code == 302
    assert p.status == St.AWAITING_UPLOAD  # faltam obrigatórios


def test_concluir_completo_avanca_para_processing(client):
    p = _pedido()
    for i, cat in enumerate(CATEGORIAS_OBRIGATORIAS):
        MidiaAsset.objects.create(
            pedido=p, categoria=cat, s3_key=f"{p.numero}/{cat}/{i}", status=StatusMidia.RECEBIDO
        )
    client.post(reverse("uploads:concluir", args=[p.numero]))
    p.refresh_from_db()
    assert p.status == St.PROCESSING
    assert p.transicoes.filter(para_status=St.PROCESSING).exists()
