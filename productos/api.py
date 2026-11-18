from rest_framework import generics
from .models import Producto
from .serializers import ProductoSerializer


class ProductoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Producto.objects.all().order_by('id')
    serializer_class = ProductoSerializer


class ProductoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
