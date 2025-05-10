# appProtectiOn/views.py
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms      import UserCreationForm
from django.contrib.auth            import login as auth_login
from django.shortcuts               import render, get_object_or_404, redirect

from rest_framework.generics       import ListCreateAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions    import IsAuthenticated
from rest_framework.parsers        import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token

from .models      import Alerta
from .serializers import AlertaSerializer

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
#                VISTAS HTML
# ------------------------------------------------------------------

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
    alerta_data = {"lat": float(alerta.lat), "lng": float(alerta.lng)}
    return render(request, 'alertas/detalle.html', {
        'alerta': alerta,
        'alerta_data': alerta_data,
    })


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# ------------------------------------------------------------------
#                API REST para ESP32
# ------------------------------------------------------------------

class AlertaListCreate(ListCreateAPIView):
    """
    Endpoint que recibe alertas (multipart) desde el ESP32.
    """
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]
    parser_classes         = [MultiPartParser, FormParser]

    def get_queryset(self):
        return (
            Alerta.objects
            .filter(usuario=self.request.user)
            .order_by('-timestamp')
        )

    def perform_create(self, serializer):
        # Import aquí → se evalúa con settings ya cargados
        from django.core.files.storage import default_storage
        import warnings
        warnings.warn(
            f"STORAGE EN RUNTIME -> {default_storage.__class__}",
            RuntimeWarning,
        )

        audio = self.request.FILES.get("audio")

        print("FILES keys =", list(self.request.FILES.keys()), flush=True)
        print(
            "audio:", getattr(audio, "name", None),
            "size:", getattr(audio, "size", None),
            flush=True,
        )
        print(
            "DATA lat=", self.request.data.get("lat"),
            "lng=", self.request.data.get("lng"),
            flush=True,
        )

        alerta = serializer.save(usuario=self.request.user)

        print("S3 URL =", alerta.audio.url, flush=True)


class AlertaRetrieve(RetrieveAPIView):
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(usuario=self.request.user)
