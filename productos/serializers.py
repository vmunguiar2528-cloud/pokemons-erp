from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'categoria',
            'proveedor',
            'precio',
            'stock',
            'imagen',
            'imagen_url',
        ]

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        url = obj.imagen.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
