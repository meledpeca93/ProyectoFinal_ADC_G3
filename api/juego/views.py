
from django.shortcuts import render


def inicio_juego(request):
    """
    Muestra la pantalla principal de Buscaminas.
    """
    return render(request, "juego/inicio.html")



def resultado_demo(request):
    """
    Vista temporal para comprobar el diseño de Resultado.
    No consulta partidas reales ni calcula puntuaciones.
    """
    estados_validos = (
        "GANADA",
        "PERDIDA",
        "TIEMPO_AGOTADO",
        "ABANDONADA",
    )

    estado = request.GET.get("estado", "GANADA").upper()

    if estado not in estados_validos:
        estado = "GANADA"

    contexto = {
        "estado": estado,
        "puntuacion": 1250 if estado == "GANADA" else 0,
        "duracion": "02:35",
        "dificultad": "Intermedio",
        "casillas_descubiertas": 45,
        "banderas_colocadas": 8,
        "minas_totales": 10,
    }

    return render(request, "juego/resultado.html", contexto)
