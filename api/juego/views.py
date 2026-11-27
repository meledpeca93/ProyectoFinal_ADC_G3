
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from .services.minas import NIVELES
from django.contrib.auth.models import User
from .models import Partida
from django.shortcuts import get_object_or_404
from .models import Partida
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .services.minas import (
    generar_minas,
    construir_tablero,
    descubrir_cascada,
    verificar_victoria,
    calcular_puntaje,
    cambiar_bandera,
    NIVELES
)
from .models import Partida, Movimiento

def inicio_juego(request):
    """
    Muestra la pantalla principal de Buscaminas.
    """
    return render(request, "juego/inicio.html")

@ensure_csrf_cookie
def pantalla_juego(request):
    return render(
        request,
        "juego/tablero.html",
        {"casillas": range(64)}
    )

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




@login_required
@require_POST
def nueva_partida(request):

    try:
        datos = json.loads(request.body)
    except ValueError:
        return JsonResponse(
            {"error": "JSON invalido"},
            status=400
        )

    nivel = datos.get("nivel")

    if nivel not in NIVELES:
        return JsonResponse(
            {"error": "Nivel invalido"},
            status=400
        )

    config = NIVELES[nivel]

    estado_juego = {
        "filas": config["filas"],
        "columnas": config["columnas"],
        "minas": config["minas"],
        "descubiertas": [],
        "banderas": [],
        "tablero": [],
        "primer_movimiento": True,
    }

    partida = Partida.objects.create(
        usuario=request.user,
        dificultad=nivel,
        limite_segundos=config["tiempo"],
        estado_juego=estado_juego,
    )

    return JsonResponse({
        "ok": True,
        "partida_id": str(partida.id),
        "estado": partida.estado,
        "nivel": partida.dificultad,
        "filas": config["filas"],
        "columnas": config["columnas"],
        "minas": config["minas"],
        "tiempo": config["tiempo"],
    })

def segundos_restantes(partida):

    final = partida.fin_servidor or timezone.now()

    duracion = int(
        (final - partida.inicio_servidor).total_seconds()
    )

    return max(0, partida.limite_segundos - duracion)


def finalizar_partida(partida, estado):

    partida.estado = estado
    partida.fin_servidor = timezone.now()

    restantes = segundos_restantes(partida)

    partida.duracion_segundos = (
        partida.limite_segundos - restantes
    )

    if estado == "GANADA":

        multiplicador = NIVELES[
            partida.dificultad
        ]["multiplicador"]

        partida.puntaje = calcular_puntaje(
            restantes,
            multiplicador
        )

    else:
        partida.puntaje = 0

    partida.save()

def estado_publico(partida):

    juego = partida.estado_juego

    descubiertas = set(
        tuple(x) for x in juego["descubiertas"]
    )

    banderas = set(
        tuple(x) for x in juego["banderas"]
    )

    tablero = juego["tablero"]

    visible = []

    for f in range(juego["filas"]):

        fila = []

        for c in range(juego["columnas"]):

            if (f, c) in descubiertas:
                fila.append(tablero[f][c])

            elif (f, c) in banderas:
                fila.append("B")

            elif (
                partida.estado != "EN_CURSO"
                and tablero
                and tablero[f][c] == -1
            ):
                fila.append(-1)

            else:
                fila.append(None)

        visible.append(fila)

    return {
        "ok": True,
        "partida_id": str(partida.id),
        "estado": partida.estado,
        "dificultad": partida.dificultad,
        "tablero": visible,
        "banderas": len(banderas),
        "descubiertas": len(descubiertas),
        "movimientos": partida.movimientos,
        "segundos_restantes": segundos_restantes(partida),
        "puntaje": partida.puntaje
    }    

@login_required
@require_GET
@transaction.atomic
def estado_partida(request, partida_id):

    partida = get_object_or_404(
        Partida.objects.select_for_update(),
        id=partida_id,
        usuario=request.user
    )

    if partida.estado == "EN_CURSO":

        if segundos_restantes(partida) == 0:

            finalizar_partida(
                partida,
                "TIEMPO_AGOTADO"
            )

    return JsonResponse(estado_publico(partida))


@login_required
@require_POST
@transaction.atomic
def accion_partida(request, partida_id):

    partida = get_object_or_404(
        Partida.objects.select_for_update(),
        id=partida_id,
        usuario=request.user
    )

    try:
        datos = json.loads(request.body)
    except ValueError:
        return JsonResponse(
            {"error": "JSON invalido"},
            status=400
        )

    if not isinstance(datos, dict):
        return JsonResponse(
            {"error": "Datos invalidos"},
            status=400
        )

    fila = datos.get("f")
    columna = datos.get("c")
    tipo = datos.get("tipo")
    numero = datos.get("numero")

    juego = partida.estado_juego

    filas = juego["filas"]
    columnas = juego["columnas"]

    if (
        type(fila) is not int
        or type(columna) is not int
        or type(numero) is not int
        or numero < 1
    ):
        return JsonResponse(
            {"error": "Movimiento invalido"},
            status=400
        )

    if not (0 <= fila < filas and 0 <= columna < columnas):
        return JsonResponse(
            {"error": "Casilla fuera del tablero"},
            status=400
        )

    anterior = Movimiento.objects.filter(
        partida=partida,
        numero=numero
    ).first()

    if anterior:
        if (
            anterior.tipo == tipo
            and anterior.datos.get("f") == fila
            and anterior.datos.get("c") == columna
        ):
            return JsonResponse(
                anterior.datos.get("respuesta")
                or estado_publico(partida)
            )

        return JsonResponse(
            {"error": "Numero de movimiento repetido"},
            status=409
        )

    if partida.estado != "EN_CURSO":
        return JsonResponse(
            estado_publico(partida),
            status=409
        )

    if segundos_restantes(partida) == 0:

        finalizar_partida(partida, "TIEMPO_AGOTADO")

        return JsonResponse(
            estado_publico(partida),
            status=409
        )

    if numero != partida.movimientos + 1:
        return JsonResponse(
            {"error": "Secuencia incorrecta"},
            status=409
        )

    descubiertas = set(
        tuple(x) for x in juego["descubiertas"]
    )

    banderas = set(
        tuple(x) for x in juego["banderas"]
    )

    posicion = (fila, columna)

    estado_final = None

    # COLOCAR O QUITAR BANDERA

    if tipo == "BANDERA":

        if posicion in descubiertas:
            return JsonResponse(
                {"error": "Casilla descubierta"},
                status=400
            )

        if (
            posicion not in banderas
            and len(banderas) >= juego["minas"]
        ):
            return JsonResponse(
                {"error": "Limite de banderas"},
                status=400
            )

        banderas = cambiar_bandera(
            fila,
            columna,
            banderas
        )

    # DESCUBRIR CASILLA

    elif tipo == "DESCUBRIR":

        if posicion in banderas:
            return JsonResponse(
                {"error": "Casilla con bandera"},
                status=400
            )

        if posicion in descubiertas:
            return JsonResponse(
                {"error": "Casilla ya descubierta"},
                status=400
            )

        # GENERAR MINAS EN EL PRIMER CLIC

        if juego["primer_movimiento"]:

            minas = generar_minas(
                filas,
                columnas,
                juego["minas"],
                posicion
            )

            juego["tablero"] = construir_tablero(
                filas,
                columnas,
                minas
            )

            juego["primer_movimiento"] = False

        tablero = juego["tablero"]

        minas = {
            (f, c)
            for f in range(filas)
            for c in range(columnas)
            if tablero[f][c] == -1
        }

        # COMPROBAR DERROTA

        if posicion in minas:

            descubiertas.add(posicion)

            estado_final = "PERDIDA"

        else:

            nuevas = descubrir_cascada(
                fila,
                columna,
                tablero,
                descubiertas | banderas,
                minas
            )

            descubiertas.update(nuevas)

            # COMPROBAR VICTORIA

            if verificar_victoria(
                descubiertas,
                filas,
                columnas,
                juego["minas"]
            ):
                estado_final = "GANADA"

    else:
        return JsonResponse(
            {"error": "Accion invalida"},
            status=400
        )

    # GUARDAR CAMBIOS

    juego["descubiertas"] = [
        list(x) for x in descubiertas
    ]

    juego["banderas"] = [
        list(x) for x in banderas
    ]

    partida.estado_juego = juego
    partida.movimientos += 1

    if estado_final:
        finalizar_partida(partida, estado_final)
    else:
        partida.save()

    respuesta = estado_publico(partida)

    Movimiento.objects.create(
        partida=partida,
        numero=numero,
        tipo=tipo,
        datos={
            "f": fila,
            "c": columna,
            "respuesta": respuesta
        }
    )

    return JsonResponse(respuesta)
