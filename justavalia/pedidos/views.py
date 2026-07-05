"""Fluxo público de criação de pedido e acompanhamento.

O pagamento é tratado pelo adapter em `pagamentos/` (MockPix em dev). As transições
de estado passam sempre pela máquina de estados do Pedido.
"""

from django.shortcuts import get_object_or_404, redirect, render

from justavalia.pagamentos.service import confirmar_pagamento, iniciar_pagamento
from justavalia.pedidos.forms import PedidoForm
from justavalia.pedidos.models import Pedido


def novo_pedido(request):
    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()
            iniciar_pagamento(pedido)
            return redirect("pedidos:pagamento", numero=pedido.numero)
    else:
        form = PedidoForm()
    return render(request, "pedidos/novo.html", {"form": form})


def pagamento(request, numero: str):
    pedido = get_object_or_404(Pedido, numero=numero)
    pag = pedido.pagamentos.order_by("-criado_em").first()
    if request.method == "POST":
        # Em dev, "simular pagamento" chama o MockPix, que aprova a cobrança.
        if pag is not None:
            confirmar_pagamento(pag)
        return redirect("pedidos:status", numero=pedido.numero)
    return render(request, "pedidos/pagamento.html", {"pedido": pedido, "pagamento": pag})


def status(request, numero: str):
    pedido = get_object_or_404(Pedido, numero=numero)
    return render(
        request,
        "pedidos/status.html",
        {"pedido": pedido, "timeline": pedido.timeline()},
    )
