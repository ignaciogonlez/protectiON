# appProtectiOn/views.py
import logging
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from rest_framework.generics       import ListCreateAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions    import IsAuthenticated
from rest_framework.parsers        import FileUploadParser
from rest_framework.authtoken.models import Token

from .models      import Alerta
from .serializers import AlertaSerializer

logger = logging.getLogger(__name__)


# ────────────────────────────────────
#  VISTAS HTML
# ────────────────────────────────────
@login_required
def lista_alertas(request):
    alertas = (
        Alerta.objects
        .filter(usuario=request.user)
        .order_by('-timestamp')
    )
    token_obj, _ = Token.objects.get_or_create(user=request.user)
    return render(request, 'alertas/lista.html', {
        'alertas': alertas,
        'token'  : token_obj.key,
    })


@login_required
def detalle_alerta(request, pk):
    alerta = get_object_or_404(
        Alerta,
        pk=pk,
        usuario=request.user
    )
    alerta_data = {
        "lat": float(alerta.lat),
        "lng": float(alerta.lng),
    }
    return render(request, 'alertas/detalle.html', {
        'alerta'     : alerta,
        'alerta_data': alerta_data,
    })


def signup(request):
    from django.contrib.auth.forms import UserCreationForm
    from django.contrib.auth       import login as auth_login

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# ────────────────────────────────────
#  API para ESP32
# ────────────────────────────────────
class AlertaListCreate(ListCreateAPIView):
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]
    parser_classes         = [FileUploadParser]  # fuerza DRF a parsear como fichero

    def get_queryset(self):
        return (
            Alerta.objects
            .filter(usuario=self.request.user)
            .order_by('-timestamp')
        )

    def perform_create(self, serializer):
        # 0) Debug – qué storage se está usando realmente
        logger.warning(">>> DEFAULT STORAGE = %s", default_storage.__class__)

        # 1) Bytes RAW del cuerpo que envía el ESP32
        wav_bytes = self.request.body
        if not wav_bytes:
            logger.error("Petición sin cuerpo: no se guardará audio")
            serializer.save(usuario=self.request.user)
            return

        # 2) Construye un ContentFile (Django File) con nombre único
        filename   = f"{uuid4()}.wav"
        audio_file = ContentFile(wav_bytes, name=filename)

        # 3) Guarda la Alerta incluyendo el fichero
        serializer.save(usuario=self.request.user, audio=audio_file)


class AlertaRetrieve(RetrieveAPIView):
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(usuario=self.request.user)
