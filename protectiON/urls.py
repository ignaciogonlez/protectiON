# protectiON/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as drf_views
from appProtectiOn import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Registro de usuarios
    path('signup/', views.signup, name='signup'),

    # Login / Logout / Cambio de contraseña (incluye password_change y password_change/done)
    path('accounts/', include('django.contrib.auth.urls')),

    # API REST
    path('api/token/', drf_views.obtain_auth_token, name='token'),
    path('api/alertas/', views.AlertaListCreate.as_view(), name='alertas-list'),
    path('api/alertas/<int:pk>/', views.AlertaRetrieve.as_view(), name='alertas-detalle'),

    # Vistas web
    path('', views.lista_alertas, name='home'),
    path('alertas/<int:pk>/', views.detalle_alerta, name='alerta-detalle'),
]
