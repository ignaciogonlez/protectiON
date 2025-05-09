# appProtectiOn/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts        import render, get_object_or_404, redirect

from rest_framework.generics       import ListCreateAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions    import IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth       import login as auth_login

from .models      import Alerta
from .serializers import AlertaSerializer

from django.core.files.storage import default_storage
import logging

logger = logging.getLogger(__name__)


# ----------  VISTAS HTML para usuarios  ----------

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

    # Solo los datos serializables que necesitamos en JS
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


# ----------  VISTAS API REST para el ESP32  ----------

from django.core.files.uploadedfile import UploadedFile

class AlertaListCreate(ListCreateAPIView):
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(
            usuario=self.request.user
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        # ← IMPORTANTE: estas tres líneas deben ir
        #     a 4 espacios de indent dentro del método
        logger.warning("FILES keys: %s", list(self.request.FILES.keys()))
        logger.warning(
            "audio?: %s",
            isinstance(self.request.FILES.get("audio"), UploadedFile)
        )
        logger.warning("storage: %s", default_storage.__class__)

        serializer.save(usuario=self.request.user)



class AlertaRetrieve(RetrieveAPIView):
    serializer_class       = AlertaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(usuario=self.request.user)
