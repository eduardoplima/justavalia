from django.contrib import admin
from django.urls import include, path

from justavalia.core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", views.healthz, name="healthz"),
    path("readyz/", views.readyz, name="readyz"),
    path("", include("justavalia.pedidos.urls")),
    path("", include("justavalia.site_publico.urls")),
]
