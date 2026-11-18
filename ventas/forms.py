from django import forms
from .models import Venta
from productos.models import Producto

class VentaForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True, stock__gt=0),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    monto_pagado = forms.DecimalField(
        required=False,
        decimal_places=2,
        label="Total a pagar",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'step': '0.01',
        })
    )
    referencia_transferencia = forms.CharField(
        required=False,
        max_length=100,
        label="Referencia de transferencia",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_tarjeta = forms.CharField(
        required=False,
        max_length=19,
        label="Número de tarjeta",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'inputmode': 'numeric',
            'autocomplete': 'cc-number',
            'placeholder': 'Ej. 4242 4242 4242 4242',
        })
    )

    class Meta:
        model = Venta
        fields = [
            'cliente', 'producto', 'cantidad', 'metodo_pago',
            'monto_pagado', 'referencia_transferencia', 'numero_tarjeta',
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {'metodo_pago': 'Método de pago'}

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        metodo_pago = cleaned_data.get('metodo_pago')

        if producto and cantidad:
            cleaned_data['monto_pagado'] = producto.precio * cantidad

        if metodo_pago == 'transferencia':
            if not cleaned_data.get('referencia_transferencia'):
                self.add_error(
                    'referencia_transferencia',
                    'Ingresa la referencia de la transferencia.',
                )

        if metodo_pago == 'tarjeta':
            numero = ''.join(
                caracter for caracter in cleaned_data.get('numero_tarjeta', '')
                if caracter.isdigit()
            )
            if len(numero) < 13 or len(numero) > 19:
                self.add_error(
                    'numero_tarjeta',
                    'Ingresa un número de tarjeta válido.',
                )
            else:
                cleaned_data['ultimos4_tarjeta'] = numero[-4:]

        return cleaned_data