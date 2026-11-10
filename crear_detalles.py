import os

os.makedirs('templates/clientes', exist_ok=True)
os.makedirs('templates/productos', exist_ok=True)
os.makedirs('templates/proveedores', exist_ok=True)

det_cli = """{% extends "base.html" %}

{% block title %}Detalle de Cliente — ERP{% endblock %}

{% block content %}
<div style="background: white; padding: 2rem; border-radius: 8px; max-width: 600px; margin: 2rem auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <h2>👤 {{ cliente.nombre }}</h2>
    <hr style="margin: 1rem 0; border: none; border-top: 1px solid #eee;">
    <p><strong>ID:</strong> #{{ cliente.id }}</p>
    <p><strong>Correo:</strong> {{ cliente.correo }}</p>
    <p><strong>Teléfono:</strong> {{ cliente.telefono|default:"No registrado" }}</p>

    <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem;">
        <a href="{% url 'clientes:editar' cliente.id %}" style="background: #ffc107; color: black; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none;">✏️ Editar</a>
        <a href="{% url 'clientes:lista' %}" style="background: #6c757d; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none;">⬅️ Volver</a>
    </div>
</div>
{% endblock %}"""

det_prod = """{% extends "base.html" %}

{% block title %}Detalle de Producto — ERP{% endblock %}

{% block content %}
<div style="background: white; padding: 2rem; border-radius: 8px; max-width: 600px; margin: 2rem auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <h2>📦 {{ producto.nombre }}</h2>
    <hr style="margin: 1rem 0; border: none; border-top: 1px solid #eee;">
    <p><strong>ID:</strong> #{{ producto.id }}</p>
    <p><strong>Categoría:</strong> {{ producto.categoria.nombre|default:"Sin categoría" }}</p>
    <p><strong>Proveedor:</strong> {{ producto.proveedor.nombre|default:"Sin proveedor" }}</p>
    <p><strong>Precio:</strong> ${{ producto.precio }}</p>
    <p><strong>Stock disponible:</strong> {{ producto.stock }} unidades</p>

    <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem;">
        <a href="{% url 'productos:editar' producto.id %}" style="background: #ffc107; color: black; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none;">✏️ Editar</a>
        <a href="{% url 'productos:lista' %}" style="background: #6c757d; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none;">⬅️ Volver</a>
    </div>
</div>
{% endblock %}"""

det_prov = """{% extends "base.html" %}

{% block title %}Detalle de Proveedor — ERP{% endblock %}

{% block content %}
<div style="background: white; padding: 2rem; border-radius: 8px; max-width: 600px; margin: 2rem auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <h2>🏭 {{ proveedor.nombre }}</h2>
    <hr style="margin: 1rem 0; border: none; border-top: 1px solid #eee;">
    <p><strong>ID:</strong> #{{ proveedor.id }}</p>
    <p><strong>Empresa:</strong> {{ proveedor.empresa|default:"Particular" }}</p>
    <p><strong>Correo:</strong> {{ proveedor.correo }}</p>
    <p><strong>Teléfono:</strong> {{ proveedor.telefono|default:"No registrado" }}</p>

    <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem;">
        <a href="{% url 'proveedores:editar' proveedor.id %}" style="background: #ffc107; color: black; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none;">✏️ Editar</a>
        <a href="{% url 'proveedores:lista' %}" style="background: #6c757d; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none;">⬅️ Volver</a>
    </div>
</div>
{% endblock %}"""

with open('templates/clientes/detalle.html', 'w', encoding='utf-8') as f:
    f.write(det_cli)

with open('templates/productos/detalle.html', 'w', encoding='utf-8') as f:
    f.write(det_prod)

with open('templates/proveedores/detalle.html', 'w', encoding='utf-8') as f:
    f.write(det_prov)

print('¡Plantillas detalle.html creadas exitosamente sin ningún error!')