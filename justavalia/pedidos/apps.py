from django.apps import AppConfig


class PedidosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "justavalia.pedidos"
    label = "pedidos"
    verbose_name = "pedidos: modelo Pedido, maquina de estados e timeline"
