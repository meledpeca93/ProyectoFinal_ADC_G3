from django.urls import include, path

from cuentas.urls import pantalla_acceso
from cuentas.views import perfil

from .views import salud

urlpatterns = [
    path("", pantalla_acceso, name="inicio"),
    path("cuentas/", include("cuentas.urls")),
    path("perfil/", perfil, name="perfil"),
    path("salud/", salud, name="salud"),
]
