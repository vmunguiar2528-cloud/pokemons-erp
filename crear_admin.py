import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Usuario y contraseña exactamente como los ingresarás
USERNAME = 'victor'
PASSWORD = 'vict0rwapo'

# Busca el usuario o lo crea
user, created = User.objects.get_or_create(username=USERNAME)
user.email = 'v.munguiar.2528@cbtis198.edu.mx'
user.set_password('vict0rwapo')
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()

print(f"==========================================")
print(f"USUARIO '{USERNAME}' CONFIGURADO CORRECTAMENTE")
print(f"==========================================")