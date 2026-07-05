"""Styleguide interno (Fase 1): só é servido quando SHOW_STYLEGUIDE está ativo."""

from django.test import override_settings


@override_settings(SHOW_STYLEGUIDE=True)
def test_styleguide_habilitado_retorna_200_com_tokens(client):
    resp = client.get("/styleguide/")
    assert resp.status_code == 200
    assert "#B4611F" in resp.content.decode()


@override_settings(SHOW_STYLEGUIDE=False)
def test_styleguide_desabilitado_retorna_404(client):
    resp = client.get("/styleguide/")
    assert resp.status_code == 404
