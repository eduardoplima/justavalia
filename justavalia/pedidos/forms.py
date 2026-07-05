from django import forms

from justavalia.pedidos.models import Pedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente_nome", "cliente_email", "cliente_whatsapp", "endereco_imovel"]
        labels = {
            "cliente_nome": "Seu nome",
            "cliente_email": "E-mail",
            "cliente_whatsapp": "WhatsApp",
            "endereco_imovel": "Endereço do imóvel",
        }
        widgets = {
            "cliente_nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "cliente_email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "cliente_whatsapp": forms.TextInput(attrs={"autocomplete": "tel"}),
            "endereco_imovel": forms.TextInput(),
        }
