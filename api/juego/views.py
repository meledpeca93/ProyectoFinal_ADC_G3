import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Movimiento, Partida
from .services.minas import (
    NIVELES,
    calcular_puntaje,
    cambiar_bandera,
    construir_tablero,
    descubrir_cascada,
    generar_minas,
    verificar_victoria,
)


NIVELES_CONFIG = {
    "facil": {
        "nombre": "Fácil",
        "filas": 8,
        "columnas": 8,
        "minas": 10,
        "limite_segundos": 240,
        "multiplicador": 1.0,
    },
    "normal": {
        "nombre": "Normal",
        "filas": 10,
        "columnas": 10,
        "minas": 18,
        "limite_segundos": 360,
        "multiplicador": 1.5,
    },
    "dificil": {
        "nombre": "Difícil",
        "filas": 12,
        "columnas": 12,
        "minas": 30,
        "limite_segundos": 480,
        "multiplicador": 2.0,
    },
}

DESENLACES_RESULTADO = {
    "GANADA": (
        "¡Partida ganada!",
        "¡Excelente! Completaste el tablero y marcaste todas las minas.",
        "trofeo",
    ),
    "PERDIDA": (
        "¡Partida perdida!",
        "Descubriste una mina antes de completar el tablero.",
        "mina",
    ),
    "TIEMPO_AGOTADO": (
        "Tiempo agotado",
        "Se agotó el tiempo límite antes de descubrir todas las casillas seguras.",
        "reloj",
    ),
    "ABANDONADA": (
        "Partida abandonada",
        "La partida finalizó por abandono antes de completarse.",
        "mando",
    ),
}

# Posiciones de minas determinísticas para la vista de demostración,
# asegurando primera zona 3x3 libre alrededor de (3, 3) y números reales consistentes.
MINAS_DEMO = {
    "facil": (
        (0, 5), (0, 7), (1, 1), (1, 6), (2, 7),
        (4, 0), (5, 2), (6, 5), (7, 1), (7, 6),
    ),
    "normal": (
        (0, 2), (0, 4), (0, 6), (0, 8), (1, 3), (1, 5),
        (1, 8), (2, 4), (2, 7), (2, 9), (3, 9), (4, 0),
        (4, 1), (5, 1), (6, 0), (7, 1), (8, 0), (9, 8),
    ),
    "dificil": (
        (0, 2), (0, 5), (0, 8), (0, 11), (1, 3), (1, 6),
        (1, 9), (2, 1), (2, 10), (3, 0), (3, 11), (4, 1),
        (4, 8), (5, 0), (5, 7), (5, 11), (6, 2), (6, 9),
        (7, 1), (7, 10), (8, 0), (8, 6), (8, 11), (9, 2),
        (9, 8), (10, 1), (10, 5), (10, 10), (11, 3), (11, 9),
    ),
}


def _obtener_rutas_navegacion():
    inicio_url = _resolver_ruta("inicio", "/")
    return {
        "inicio": inicio_url,
        "como_jugar": _resolver_ruta("instrucciones", f"{inicio_url}#caracteristicas"),
        "clasificacion": _resolver_ruta("clasificacion", f"{inicio_url}#caracteristica-puntajes"),
        "historial": _resolver_ruta("historial", _resolver_ruta("perfil", "/perfil/")),
        "nueva_partida": _resolver_ruta("pantalla_juego", f"{inicio_url}#jugar"),
        "jugar": _resolver_ruta("pantalla_juego", ""),
        "perfil": _resolver_ruta("perfil", "/perfil/"),
    }


def inicio_juego(request):
    """Muestra la pantalla principal de Buscaminas."""
    dificultad = request.GET.get("nivel", "normal").lower()
    if dificultad not in NIVELES_CONFIG:
        dificultad = "normal"

    niveles = [
        {
            "clave": clave,
            "nombre": datos["nombre"],
            "filas": datos["filas"],
            "columnas": datos["columnas"],
            "minas": datos["minas"],
            "limite_segundos": datos["limite_segundos"],
        }
        for clave, datos in NIVELES_CONFIG.items()
    ]

    rutas = _obtener_rutas_navegacion()
    return render(request, "juego/inicio.html", {
        "niveles": niveles,
        "dificultad_seleccionada": dificultad,
        "nombre_jugador": _obtener_nombre_jugador(request.user),
        "rutas": rutas,
    })


def formatear_tiempo(segundos):
    """Convierte segundos enteros a formato MM:SS."""
    total = max(0, int(segundos or 0))
    minutos, resto = divmod(total, 60)
    return f"{minutos:02d}:{resto:02d}"


def calcular_puntaje_oficial(estado, dificultad, duracion_segundos):
    """Aplica la fórmula oficial del servidor para el puntaje final."""
    if estado != "GANADA":
        return 0
    config = NIVELES_CONFIG[dificultad]
    restantes = max(0, config["limite_segundos"] - int(duracion_segundos))
    return round((800 + 3 * restantes) * config["multiplicador"])


def _contar_vecinas(filas, columnas, minas_set, fila, col):
    total = 0
    for df in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if df == 0 and dc == 0:
                continue
            nf, nc = fila + df, col + dc
            if 0 <= nf < filas and 0 <= nc < columnas and (nf, nc) in minas_set:
                total += 1
    return total


def construir_tablero_final(
    filas,
    columnas,
    minas,
    estado,
    descubiertas=None,
    banderas=None,
    mina_explotada=None,
):
    """Construye la matriz de celdas para el tablero final con valores consistentes."""
    minas_set = {tuple(pos) for pos in minas}
    banderas_set = {tuple(pos) for pos in (banderas or ())}

    if descubiertas is None:
        if estado == "GANADA":
            descubiertas_set = {
                (f, c)
                for f in range(filas)
                for c in range(columnas)
                if (f, c) not in minas_set
            }
        else:
            descubiertas_set = {
                (f, c)
                for f in range(filas)
                for c in range(columnas)
                if (f, c) not in minas_set and (f + c) % 3 != 0 and f < filas - 1
            }
    else:
        descubiertas_set = {tuple(pos) for pos in descubiertas}

    matriz = []
    for f in range(filas):
        fila_celdas = []
        for c in range(columnas):
            coord = (f, c)
            es_mina = coord in minas_set
            tiene_bandera = coord in banderas_set
            esta_descubierta = coord in descubiertas_set

            if mina_explotada and coord == tuple(mina_explotada):
                tipo = "mina-explotada"
                numero = None
            elif es_mina and estado != "GANADA" and not tiene_bandera:
                tipo = "mina"
                numero = None
            elif tiene_bandera:
                tipo = "bandera-error" if (estado != "GANADA" and not es_mina) else "bandera"
                numero = None
            elif esta_descubierta and not es_mina:
                tipo = "descubierta"
                numero = _contar_vecinas(filas, columnas, minas_set, f, c)
            else:
                tipo = "oculta"
                numero = None

            fila_celdas.append({
                "fila": f,
                "columna": c,
                "tipo": tipo,
                "numero": numero,
            })
        matriz.append(fila_celdas)
    return matriz


def evaluar_logros(estado, dificultad, duracion_segundos, todas_minas_marcadas):
    """Calcula los logros obtenidos según reglas reales de la partida."""
    victoria = estado == "GANADA"
    cumple_normal = victoria and dificultad == "normal"
    cumple_rapido = victoria and duracion_segundos < 300
    cumple_detector = victoria and bool(todas_minas_marcadas)

    return [
        {
            "icono": "rayo",
            "svg": "img/resultados/achievement-lightning.svg",
            "titulo": "Victoria en Normal",
            "descripcion": "Completa un tablero en nivel Normal.",
            "cumplido": cumple_normal,
        },
        {
            "icono": "reloj",
            "svg": "img/resultados/achievement-stopwatch.svg",
            "titulo": "Juego rápido",
            "descripcion": "Termina en menos de 5 minutos.",
            "cumplido": cumple_rapido,
        },
        {
            "icono": "bandera",
            "svg": "img/resultados/achievement-flag.svg",
            "titulo": "Detector de minas",
            "descripcion": "Marca correctamente todas las minas.",
            "cumplido": cumple_detector,
        },
    ]


def _resolver_ruta(nombre_url, fallback):
    try:
        return reverse(nombre_url)
    except NoReverseMatch:
        return fallback


def construir_contexto_resultado(
    *,
    estado,
    dificultad,
    duracion_segundos,
    movimientos,
    banderas_colocadas,
    seguras_descubiertas,
    tablero_matriz,
    puntaje_actual=None,
    mejor_previo=None,
    todas_minas_marcadas=False,
    es_demo=False,
):
    """Prepara el diccionario de contexto completo para la plantilla de resultado."""
    estado = estado if estado in DESENLACES_RESULTADO else "GANADA"
    dificultad = dificultad if dificultad in NIVELES_CONFIG else "normal"
    config = NIVELES_CONFIG[dificultad]

    titulo, mensaje, icono_estado = DESENLACES_RESULTADO[estado]
    mensaje_enfasis = ""
    if estado == "GANADA":
        if todas_minas_marcadas:
            mensaje = "¡Excelente! Completaste el tablero y"
            mensaje_enfasis = "marcaste todas las minas."
        else:
            mensaje = "¡Excelente! Descubriste todas las casillas seguras del tablero."

    seguras_total = config["filas"] * config["columnas"] - config["minas"]
    if puntaje_actual is None:
        puntaje_actual = calcular_puntaje_oficial(estado, dificultad, duracion_segundos)

    logros = evaluar_logros(estado, dificultad, duracion_segundos, todas_minas_marcadas)

    puntaje_previo = mejor_previo["puntaje"] if mejor_previo else None
    es_nuevo_record = estado == "GANADA" and (
        puntaje_previo is None or puntaje_actual > puntaje_previo
    )
    diferencia_record = (
        puntaje_actual - puntaje_previo
        if es_nuevo_record and puntaje_previo is not None
        else 0
    )

    rutas = _obtener_rutas_navegacion()

    return {
        "es_demo": es_demo,
        "estado": estado,
        "dificultad": dificultad,
        "nivel_nombre": config["nombre"],
        "titulo": titulo,
        "mensaje": mensaje,
        "mensaje_enfasis": mensaje_enfasis,
        "icono_estado": icono_estado,
        "filas": config["filas"],
        "columnas": config["columnas"],
        "minas_total": config["minas"],
        "tiempo_formateado": formatear_tiempo(duracion_segundos),
        "duracion_segundos": duracion_segundos,
        "movimientos": movimientos,
        "banderas": banderas_colocadas,
        "seguras_descubiertas": seguras_descubiertas,
        "seguras_total": seguras_total,
        "puntaje_final": puntaje_actual,
        "tablero_matriz": tablero_matriz,
        "logros": logros,
        "logros_obtenidos": sum(1 for logro in logros if logro["cumplido"]),
        "comparativa": {
            "tiene_previo": mejor_previo is not None,
            "previo_puntaje": mejor_previo["puntaje"] if mejor_previo else None,
            "previo_tiempo": (
                formatear_tiempo(mejor_previo["duracion_segundos"])
                if mejor_previo
                else "—"
            ),
            "previo_movimientos": mejor_previo["movimientos"] if mejor_previo else "—",
            "actual_puntaje": puntaje_actual,
            "actual_tiempo": formatear_tiempo(duracion_segundos),
            "actual_movimientos": movimientos,
            "es_nuevo_record": es_nuevo_record,
            "diferencia_record": diferencia_record,
        },
        "rutas": rutas,
    }


def resultado_demo(request):
    """Vista de demostración con tablero, métricas y comparativa coherentes."""
    estado = request.GET.get("estado", "GANADA").upper()
    if estado not in DESENLACES_RESULTADO:
        estado = "GANADA"

    dificultad = request.GET.get("nivel", "normal").lower()
    if dificultad not in NIVELES_CONFIG:
        dificultad = "normal"

    config = NIVELES_CONFIG[dificultad]
    minas = MINAS_DEMO[dificultad]
    filas, columnas = config["filas"], config["columnas"]
    seguras_total = filas * columnas - config["minas"]

    if estado == "GANADA":
        duracion_default = {"facil": 142, "normal": 262, "dificil": 348}[dificultad]
        duracion = duracion_default
        movimientos = {"facil": 41, "normal": 61, "dificil": 89}[dificultad]
        banderas = minas
        descubiertas = None
        mina_explotada = None
        todas_marcadas = True
    else:
        duracion = {"facil": 95, "normal": 184, "dificil": 240}[dificultad]
        if estado == "TIEMPO_AGOTADO":
            duracion = config["limite_segundos"]
        movimientos = {"facil": 23, "normal": 39, "dificil": 54}[dificultad]
        banderas = minas[: max(2, len(minas) // 3)]
        mina_explotada = minas[0] if estado == "PERDIDA" else None
        descubiertas = [
            (f, c)
            for f in range(filas)
            for c in range(columnas)
            if (f, c) not in set(minas) and (f + c) % 3 != 0 and f < filas - 1
        ]
        todas_marcadas = False

    tablero_matriz = construir_tablero_final(
        filas=filas,
        columnas=columnas,
        minas=minas,
        estado=estado,
        descubiertas=descubiertas,
        banderas=banderas,
        mina_explotada=mina_explotada,
    )

    seguras_descubiertas = sum(
        1
        for fila_celdas in tablero_matriz
        for celda in fila_celdas
        if celda["tipo"] == "descubierta"
    )
    banderas_colocadas = sum(
        1
        for fila_celdas in tablero_matriz
        for celda in fila_celdas
        if celda["tipo"] in ("bandera", "bandera-error")
    )

    puntaje_calculado = calcular_puntaje_oficial(estado, dificultad, duracion)
    forzar_sin_record = request.GET.get("record") == "0"
    if forzar_sin_record:
        mejor_previo = {
            "puntaje": max(puntaje_calculado + 45, 1720),
            "duracion_segundos": max(60, duracion - 18),
            "movimientos": max(15, movimientos - 5),
        }
    else:
        mejor_previo = {
            "puntaje": max(100, (puntaje_calculado or 1608) - 35),
            "duracion_segundos": duracion + 12,
            "movimientos": movimientos + 2,
        }

    contexto = construir_contexto_resultado(
        estado=estado,
        dificultad=dificultad,
        duracion_segundos=duracion,
        movimientos=movimientos,
        banderas_colocadas=banderas_colocadas,
        seguras_descubiertas=seguras_descubiertas,
        tablero_matriz=tablero_matriz,
        puntaje_actual=puntaje_calculado,
        mejor_previo=mejor_previo,
        todas_minas_marcadas=todas_marcadas,
        es_demo=True,
    )
    contexto["seguras_total"] = seguras_total
    contexto["nombre_jugador"] = _obtener_nombre_jugador(request.user)
    return render(request, "juego/resultado.html", contexto)


def _obtener_nombre_jugador(user):
    if not getattr(user, "is_authenticated", False):
        return ""
    try:
        alias = user.perfil_jugador.alias
    except Exception:
        alias = ""
    return alias or user.get_full_name() or user.username


@login_required
@ensure_csrf_cookie
@require_GET
def pantalla_juego(request):
    nivel = request.GET.get("nivel", "normal").lower()
    if nivel not in NIVELES_CONFIG:
        nivel = "normal"
    return render(request, "juego/tablero.html", {
        "casillas": range(64),
        "nivel_inicial": nivel.upper(),
    })


@login_required
@require_GET
def resultado_partida(request, partida_id):
    partida = get_object_or_404(
        Partida, pk=partida_id, usuario=request.user, estado__in=DESENLACES_RESULTADO,
    )
    juego = partida.estado_juego
    minas = {
        (f, c)
        for f, fila in enumerate(juego["tablero"])
        for c, valor in enumerate(fila)
        if valor == -1
    }
    descubiertas = {tuple(posicion) for posicion in juego["descubiertas"]}
    banderas = {tuple(posicion) for posicion in juego["banderas"]}
    tablero = construir_tablero_final(
        filas=juego["filas"], columnas=juego["columnas"], minas=minas,
        estado=partida.estado, descubiertas=descubiertas, banderas=banderas,
        mina_explotada=next(iter(descubiertas & minas), None),
    )
    anterior = (
        Partida.objects.filter(
            usuario=request.user, dificultad=partida.dificultad, estado="GANADA",
            fin_servidor__lt=partida.fin_servidor,
        )
        .order_by("-puntaje", "duracion_segundos", "fin_servidor")
        .values("puntaje", "duracion_segundos", "movimientos")
        .first()
        if partida.fin_servidor else None
    )
    contexto = construir_contexto_resultado(
        estado=partida.estado, dificultad=partida.dificultad.lower(),
        duracion_segundos=partida.duracion_segundos, movimientos=partida.movimientos,
        banderas_colocadas=len(banderas), seguras_descubiertas=len(descubiertas - minas),
        tablero_matriz=tablero, puntaje_actual=partida.puntaje, mejor_previo=anterior,
        todas_minas_marcadas=bool(minas) and minas == banderas,
    )
    contexto["nombre_jugador"] = _obtener_nombre_jugador(request.user)
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
        "puntaje": partida.puntaje,
        "resultado_url": (
            reverse("resultado_partida", kwargs={"partida_id": partida.pk})
            if partida.estado != "EN_CURSO" else None
        ),
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

@login_required
@require_POST
@transaction.atomic
def abandonar_partida(request, partida_id):

    partida = get_object_or_404(
        Partida.objects.select_for_update(),
        id=partida_id,
        usuario=request.user
    )

    if partida.estado == "EN_CURSO":

        if segundos_restantes(partida) == 0:

            finalizar_partida(partida, "TIEMPO_AGOTADO")

        else:

            finalizar_partida(partida, "ABANDONADA")

    return JsonResponse(estado_publico(partida))
