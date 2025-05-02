# appProtectiOn/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login

from .models import Alerta
from .serializers import AlertaSerializer

# ----------  VISTAS HTML para usuarios  ----------

@login_required
def lista_alertas(request):
    alertas = (
        Alerta.objects
        .filter(usuario=request.user)
        .order_by('-timestamp')
    )
    # Obtener (o crear) token para este usuario
    token_obj, _ = Token.objects.get_or_create(user=request.user)
    return render(request, 'alertas/lista.html', {
        'alertas': alertas,
        'token': token_obj.key,
    })


@login_required
def detalle_alerta(request, pk):
    alerta = get_object_or_404(
        Alerta,
        pk=pk,
        usuario=request.user
    )
    return render(request, 'alertas/detalle.html', {'alerta': alerta})


def signup(request):
    """
    Registro de nuevos usuarios.
    """
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

class AlertaListCreate(ListCreateAPIView):
    """
    GET  -> lista de alertas propias (descendente)
    POST -> crea alerta nueva (lat, lng, audio)
    """
    serializer_class        = AlertaSerializer
    authentication_classes  = [TokenAuthentication]
    permission_classes      = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(usuario=self.request.user).order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class AlertaRetrieve(RetrieveAPIView):
    """
    GET /api/alertas/<pk>/  -> detalle JSON de UNA alerta
    """
    serializer_class        = AlertaSerializer
    authentication_classes  = [TokenAuthentication]
    permission_classes      = [IsAuthenticated]

    def get_queryset(self):
        return Alerta.objects.filter(usuario=self.request.user)
