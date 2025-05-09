# appProtectiOn/signals.py
import os

from django.db.models.signals import post_migrate
from django.dispatch          import receiver
from django.contrib.auth      import get_user_model


@receiver(post_migrate)
def create_default_superuser(sender, **kwargs):
    """
    Se ejecuta una vez tras 'migrate'.  
    Crea el superusuario con las variables de entorno solo si todavía no existe.
    """
    User = get_user_model()

    username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    email    = os.getenv("DJANGO_SUPERUSER_EMAIL")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

    if not all([username, email, password]):
        return

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username,
                                      email=email,
                                      password=password)
