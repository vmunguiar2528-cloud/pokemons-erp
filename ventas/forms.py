from django import forms
from .models import Venta
from productos.models import Producto

class VentaForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Venta
        fields = ['cliente', 'producto', 'cantidad']