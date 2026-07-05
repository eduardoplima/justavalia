from django.urls import path

from justavalia.pedidos import views

app_name = "pedidos"

urlpatterns = [
    path("pedido/novo/", views.novo_pedido, name="novo"),
    path("pedido/<str:numero>/pagamento/", views.pagamento, name="pagamento"),
    path("pedido/<str:numero>/", views.status, name="status"),
]
