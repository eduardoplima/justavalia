from django.contrib import admin

from justavalia.uploads.models import MidiaAsset


@admin.register(MidiaAsset)
class MidiaAssetAdmin(admin.ModelAdmin):
    list_display = ("pedido", "categoria", "status", "tamanho_bytes", "recebido_em")
    list_filter = ("categoria", "status")
    search_fields = ("pedido__numero", "s3_key", "nome_original")
    readonly_fields = ("criado_em", "recebido_em", "etag", "sha256", "upload_id")
