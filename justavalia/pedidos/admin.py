from django.contrib import admin

from justavalia.pedidos.models import Pedido, TransicaoLog


class TransicaoLogInline(admin.TabularInline):
    model = TransicaoLog
    extra = 0
    can_delete = False
    readonly_fields = ("de_status", "para_status", "ator", "ator_desc", "motivo", "criado_em")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("numero", "status", "cliente_nome", "criado_em")
    list_filter = ("status", "tipo_imovel")
    search_fields = ("numero", "cliente_nome", "cliente_email")
    readonly_fields = ("numero", "criado_em", "atualizado_em")
    inlines = [TransicaoLogInline]


@admin.register(TransicaoLog)
class TransicaoLogAdmin(admin.ModelAdmin):
    list_display = ("pedido", "de_status", "para_status", "ator_desc", "criado_em")
    list_filter = ("para_status",)
    readonly_fields = (
        "pedido",
        "de_status",
        "para_status",
        "ator",
        "ator_desc",
        "motivo",
        "payload",
        "criado_em",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False  # log imutável

    def has_delete_permission(self, request, obj=None):
        return False
