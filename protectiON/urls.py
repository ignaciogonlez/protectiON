# protectiON/urls.py
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as drf_views
from appProtectiOn import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Registro de usuarios
    path('signup/', views.signup, name='signup'),

    # Login y logout explícitos (sin password_change)
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # API REST
    path('api/token/', drf_views.obtain_auth_token, name='token'),
    path('api/alertas/', views.AlertaListCreate.as_view(), name='alertas-list'),
    path('api/alertas/<int:pk>/', views.AlertaRetrieve.as_view(), name='alertas-detalle'),

    # Vistas web
    path('', views.lista_alertas, name='home'),
    path('alertas/<int:pk>/', views.detalle_alerta, name='alerta-detalle'),
]
