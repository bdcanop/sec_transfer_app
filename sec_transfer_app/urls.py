from django.urls import path
from .views import *

urlpatterns = [
    path('enviar', enviar_correo_view, name='enviar_correo'),
    path('', desencriptar_archivo_view, name='desencriptar_archivo'),
]