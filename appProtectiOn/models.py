# appProtectiOn/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

def audio_filename(instance, filename):
    ext = filename.split('.')[-1]
    return f'audios/{uuid.uuid4()}.{ext}'

class Alerta(models.Model):
    usuario   = models.ForeignKey(User, on_delete=models.CASCADE)
    lat       = models.FloatField()
    lng       = models.FloatField()
    audio     = models.FileField(upload_to=audio_filename)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'#{self.id} {self.usuario} {self.timestamp:%Y-%m-%d %H:%M}'
