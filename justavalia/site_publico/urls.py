from django.urls import path

from justavalia.site_publico import views

app_name = "site_publico"

urlpatterns = [
    path("styleguide/", views.styleguide, name="styleguide"),
]
