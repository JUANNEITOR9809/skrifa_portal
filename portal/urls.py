from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("ingresar/", views.ingresar, name="ingresar"),
    path("salir/", views.salir, name="salir"),
    path("proyecto/", views.proyecto, name="proyecto"),
    path("contrato/", views.contrato, name="contrato"),
    path("pagos/", views.pagos, name="pagos"),
    path("soporte/", views.soporte, name="soporte"),
    path("mis-datos/", views.datos, name="datos"),
    path("reiniciar-demo/", views.reiniciar, name="reiniciar"),
]
