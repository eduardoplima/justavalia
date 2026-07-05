from django.urls import path

from justavalia.uploads import views

app_name = "uploads"

urlpatterns = [
    path("pedido/<str:numero>/enviar/", views.enviar, name="enviar"),
    path("pedido/<str:numero>/enviar/concluir/", views.concluir, name="concluir"),
    # Contrato @uppy/aws-s3 (multipart presigned):
    path("pedido/<str:numero>/upload/s3/multipart/", views.s3_create, name="s3_create"),
    path(
        "pedido/<str:numero>/upload/s3/multipart/<str:upload_id>/complete/",
        views.s3_complete,
        name="s3_complete",
    ),
    path(
        "pedido/<str:numero>/upload/s3/multipart/<str:upload_id>/<int:part_number>/",
        views.s3_sign_part,
        name="s3_sign_part",
    ),
    path(
        "pedido/<str:numero>/upload/s3/multipart/<str:upload_id>/",
        views.s3_upload,
        name="s3_upload",
    ),
]
