from django.urls import path
from django.views.generic import TemplateView

from justavalia.site_publico import views

app_name = "site_publico"

urlpatterns = [
    path("", TemplateView.as_view(template_name="paginas/home.html"), name="home"),
    path(
        "como-funciona/",
        TemplateView.as_view(template_name="paginas/como_funciona.html"),
        name="como_funciona",
    ),
    path(
        "para-advogados/",
        TemplateView.as_view(template_name="paginas/advogados.html"),
        name="advogados",
    ),
    path(
        "quem-assina/",
        TemplateView.as_view(template_name="paginas/quem_assina.html"),
        name="quem_assina",
    ),
    path("faq/", TemplateView.as_view(template_name="paginas/faq.html"), name="faq"),
    path(
        "privacidade/",
        TemplateView.as_view(template_name="paginas/privacidade.html"),
        name="privacidade",
    ),
    path("termos/", TemplateView.as_view(template_name="paginas/termos.html"), name="termos"),
    path("styleguide/", views.styleguide, name="styleguide"),
]
