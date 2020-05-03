from django.forms import ModelForm

from core import models


class PedidoForm(ModelForm):
    class Meta:
        model = models.Pedido
        fields = '__all__'
