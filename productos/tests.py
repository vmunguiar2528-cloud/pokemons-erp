from decimal import Decimal
from io import BytesIO
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Categoria, Producto
from .serializers import ProductoSerializer


class ProductoImageTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Cartas')

    def create_valid_image(self, name='test.png', size=(50, 50), color=(255, 0, 0)):
        image = Image.new('RGB', size, color)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')

    def test_producto_guarda_imagen_valida(self):
        image = self.create_valid_image()
        producto = Producto.objects.create(
            nombre='Pikachu',
            categoria=self.categoria,
            precio=Decimal('199.99'),
            stock=10,
            imagen=image,
        )
        self.assertTrue(producto.imagen)
        self.assertIn('productos', producto.imagen.name)

    def test_imagen_tamanio_too_large_fails(self):
        large_image = SimpleUploadedFile(
            'large.png',
            b'0' * (3 * 1024 * 1024),
            content_type='image/png',
        )
        with self.assertRaises(ValidationError):
            Producto(
                nombre='Grande',
                categoria=self.categoria,
                precio=Decimal('10.00'),
                stock=5,
                imagen=large_image,
            ).full_clean()

    def test_imagen_tipo_invalido_fails(self):
        invalid_file = SimpleUploadedFile(
            'bad.txt',
            b'not an image',
            content_type='text/plain',
        )
        with self.assertRaises(ValidationError):
            Producto(
                nombre='NoImagen',
                categoria=self.categoria,
                precio=Decimal('12.00'),
                stock=4,
                imagen=invalid_file,
            ).full_clean()

    def test_serializer_incluye_imagen_url(self):
        image = self.create_valid_image()
        producto = Producto.objects.create(
            nombre='Bulbasaur',
            categoria=self.categoria,
            precio=Decimal('299.50'),
            stock=7,
            imagen=image,
        )
        serializer = ProductoSerializer(producto, context={'request': None})
        data = serializer.data
        self.assertIn('imagen_url', data)
        self.assertIn('productos/', data['imagen_url'])

    def test_api_list_returns_products(self):
        Producto.objects.create(
            nombre='Charmander',
            categoria=self.categoria,
            precio=Decimal('150.00'),
            stock=8,
            imagen=self.create_valid_image('charmander.png'),
        )
        response = self.client.get(reverse('productos:api_list_create'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)
