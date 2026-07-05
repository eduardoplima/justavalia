from django.contrib import admin

from justavalia.pagamentos.models import Pagamento


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ("txid", "pedido", "provedor", "status", "valor_centavos", "criado_em")
    list_filter = ("status", "provedor")
    search_fields = ("txid", "pedido__numero")
    readonly_fields = ("criado_em", "atualizado_em")
