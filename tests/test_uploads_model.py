"""Manifesto de mídia e checagem de completude do protocolo guiado."""

import pytest

from justavalia.pedidos.models import Pedido
from justavalia.uploads.models import (
    CATEGORIAS_OBRIGATORIAS,
    CategoriaMidia,
    MidiaAsset,
    StatusMidia,
    completude,
)

pytestmark = pytest.mark.django_db


def _pedido():
    return Pedido.objects.create(
        cliente_nome="F", cliente_email="f@example.com", endereco_imovel="R X, 1"
    )


def _midia(pedido, categoria, status=StatusMidia.RECEBIDO, key=None):
    return MidiaAsset.objects.create(
        pedido=pedido,
        categoria=categoria,
        s3_key=key or f"{pedido.numero}/{categoria}/{MidiaAsset.objects.count()}",
        status=status,
    )


def test_pedido_sem_midia_esta_incompleto():
    p = _pedido()
    r = completude(p)
    assert r["completo"] is False
    assert set(r["faltando"]) == set(CATEGORIAS_OBRIGATORIAS)


def test_pedido_com_todos_obrigatorios_esta_completo():
    p = _pedido()
    for cat in CATEGORIAS_OBRIGATORIAS:
        _midia(p, cat)
    r = completude(p)
    assert r["completo"] is True
    assert r["faltando"] == []


def test_faltando_lista_so_o_que_falta():
    p = _pedido()
    _midia(p, CategoriaMidia.FOTO_FACHADA)
    _midia(p, CategoriaMidia.VIDEO_VISTORIA)
    r = completude(p)
    assert set(r["faltando"]) == {
        CategoriaMidia.DOC_MATRICULA,
        CategoriaMidia.DOC_IPTU,
    }


def test_upload_em_andamento_nao_conta_para_completude():
    p = _pedido()
    for cat in CATEGORIAS_OBRIGATORIAS:
        _midia(p, cat, status=StatusMidia.EM_ANDAMENTO)
    r = completude(p)
    assert r["completo"] is False
    assert set(r["faltando"]) == set(CATEGORIAS_OBRIGATORIAS)


def test_complementares_nao_bloqueiam():
    # Habite-se/planta entram como DOC_COMPLEMENTAR e não são exigidos.
    p = _pedido()
    for cat in CATEGORIAS_OBRIGATORIAS:
        _midia(p, cat)
    _midia(p, CategoriaMidia.DOC_COMPLEMENTAR)
    assert completude(p)["completo"] is True
