# appProtectiOn/apps.py

import os
from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model

class AppProtectiOnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appProtectiOn'

    def ready(self):
        # Sólo en producción (DEBUG=False) o siempre si quieres
        # if not settings.DEBUG:
        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email    = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        # Si NO tienes todas las vars, no haces nada
        if not (username and email and password):
            return

        # Si el usuario ya existe, no hagas nada
        if User.objects.filter(username=username).exists():
            return

        # Crea el superusuario
        User.objects.create_superuser(username=username,
                                      email=email,
                                      password=password)
