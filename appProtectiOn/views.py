# appProtectiOn/views.py
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms      import UserCreationForm
from django.contrib.auth            import login as auth_login
from django.core.files.storage      import default_storage
from django.shortcuts               import render, get_object_or_404, redirect

from rest_framework.generics       import ListCreateAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions    import IsAuthenticated
from rest_framework.parsers        import MultiPartParser, FormParser      # 👈 NUEVO
from rest_framework.authtoken.models import Token

from django.core.files.uploadedfile import UploadedFile

from .models      import Alerta
from .serializers import AlertaSerializer

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
#                VISTAS HTML PARA USUARIOS (web)
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

    # Solo los datos serializables que necesitamos en JS
    alerta_data = {
        "lat": float(alerta.lat),
        "lng": float(alerta.lng),
    }

    return render(request, 'alertas/detalle.html', {
        'alerta'     : alerta,
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
#                VISTAS API REST PARA EL ESP32
# ------------------------------------------------------------------

class AlertaListCreate(ListCreateAPIView):
    """
    Endpoint que recibe alertas desde el ESP32.
    Añadimos MultiPartParser / FormParser para asegurar que DRF trate
    la petición como multipart y podamos inspeccionar request.FILES.
    """
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]
    parser_classes         = [MultiPartParser, FormParser]      # 👈 NUEVO

    # ---------- consultas ----------

    def get_queryset(self):
        return (
            Alerta.objects
            .filter(usuario=self.request.user)
            .order_by('-timestamp')
        )

    # ---------- creación ----------

    # appProtectiOn/views.py  (solo cambio en perform_create)
    def perform_create(self, serializer):
        audio = self.request.FILES.get("audio")

        print("FILES keys =", list(self.request.FILES.keys()), flush=True)
        print(
            "audio:",
            getattr(audio, "name", None),
            "size:",
            getattr(audio, "size", None),
            flush=True,
        )
        print(
            "DATA lat=", self.request.data.get("lat"),
            "lng=", self.request.data.get("lng"),
            flush=True,
        )

        serializer.save(usuario=self.request.user)



class AlertaRetrieve(RetrieveAPIView):
    """
    Obtiene una alerta concreta.
    """
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(usuario=self.request.user)
