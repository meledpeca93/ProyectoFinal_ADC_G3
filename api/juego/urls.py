
from django.urls import path
from .views import inicio_juego, resultado_demo

urlpatterns = [
    path("", inicio_juego, name="inicio_juego"),
    path("resultado-demo/", resultado_demo, name="resultado_demo"),
]
