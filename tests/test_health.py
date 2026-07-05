"""Endpoints de saúde. readyz exercita o caminho do banco (prova migrações + conexão)."""

import pytest


def test_healthz_liveness(client):
    resp = client.get("/healthz/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
def test_readyz_banco_ok(client):
    # Sem Redis nos testes, readyz pode reportar redis=erro; o banco deve estar ok.
    resp = client.get("/readyz/")
    assert resp.json()["checks"]["database"] == "ok"
