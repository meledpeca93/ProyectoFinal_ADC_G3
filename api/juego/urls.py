
from django.urls import path
from .views import inicio_juego, resultado_demo
from django.urls import path
from .views import pantalla_juego
from .views import (
    inicio_juego,
    resultado_demo,
    nueva_partida,
    estado_partida,
    accion_partida,
    abandonar_partida,
)

urlpatterns = [
    path("", inicio_juego, name="inicio_juego"),

    path(
        "resultado-demo/",
        resultado_demo,
        name="resultado_demo"
    ),

    path(
    "jugar/",
    pantalla_juego,
    name="pantalla_juego"
    ),

    path(
        "partidas/nueva/",
        nueva_partida,
        name="nueva_partida"
    ),

    path(
        "api/partidas/<uuid:partida_id>/estado/",
        estado_partida,
        name="estado_partida"
    ),

    path(
        "api/partidas/<uuid:partida_id>/accion/",
        accion_partida,
        name="accion_partida"
    ),

        path(
        "api/partidas/<uuid:partida_id>/abandonar/",
        abandonar_partida,
        name="abandonar_partida"
    ),
]
