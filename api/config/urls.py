from django.urls import include, path

from cuentas.views import perfil
from juego.views import inicio_juego, resultado_partida

from .views import salud

urlpatterns = [
    path("", inicio_juego, name="inicio"),
    path("cuentas/", include("cuentas.urls")),
    path("perfil/", perfil, name="perfil"),
    path("salud/", salud, name="salud"),
    path("partidas/<uuid:partida_id>/resultado/", resultado_partida, name="resultado_partida"),
    path("inicio-juego/", include("juego.urls")),
]
