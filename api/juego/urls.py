from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio_juego, name="inicio_juego"),
    path("resultado-demo/", views.resultado_demo, name="resultado_demo"),
    path("jugar/", views.pantalla_juego, name="pantalla_juego"),
    path("partidas/nueva/", views.nueva_partida, name="nueva_partida"),
    path("api/partidas/<uuid:partida_id>/estado/", views.estado_partida, name="estado_partida"),
    path("api/partidas/<uuid:partida_id>/accion/", views.accion_partida, name="accion_partida"),
    path("api/partidas/<uuid:partida_id>/abandonar/", views.abandonar_partida, name="abandonar_partida"),
]
