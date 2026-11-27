import random
from collections import deque

def obtener_vecinas(fila, columna, filas, columnas):
    vecinas = []

    for df in (-1, 0, 1):
        for dc in (-1, 0, 1):

            if df == 0 and dc == 0:
                continue

            nf = fila + df
            nc = columna + dc

            if 0 <= nf < filas and 0 <= nc < columnas:
                vecinas.append((nf, nc))

    return vecinas

def generar_minas(
    filas,
    columnas,
    cantidad_minas,
    primer_click
):

    fila_click, columna_click = primer_click

    zona_segura = {
        (fila_click, columna_click)
    }

    zona_segura.update(
        obtener_vecinas(
            fila_click,
            columna_click,
            filas,
            columnas
        )
    )

    todas = [
        (f, c)
        for f in range(filas)
        for c in range(columnas)
        if (f, c) not in zona_segura
    ]

    minas = set(
        random.sample(
            todas,
            cantidad_minas
        )
    )

    return minas

def contar_minas_vecinas(
    fila,
    columna,
    minas,
    filas,
    columnas
):

    contador = 0

    for nf, nc in obtener_vecinas(
        fila,
        columna,
        filas,
        columnas
    ):

        if (nf, nc) in minas:
            contador += 1

    return contador

def construir_tablero(
    filas,
    columnas,
    minas
):

    tablero = []

    for f in range(filas):

        fila_actual = []

        for c in range(columnas):

            if (f, c) in minas:
                fila_actual.append(-1)

            else:
                valor = contar_minas_vecinas(
                    f,
                    c,
                    minas,
                    filas,
                    columnas
                )

                fila_actual.append(valor)

        tablero.append(fila_actual)

    return tablero


def descubrir_cascada(
    fila,
    columna,
    tablero,
    descubiertas,
    minas
):
    """
    Descubre automáticamente todas las casillas conectadas
    cuando se pulsa un 0.
    """

    cola = deque()
    cola.append((fila, columna))

    nuevas = set()

    while cola:

        f, c = cola.popleft()

        if (f, c) in descubiertas:
            continue

        if (f, c) in nuevas:
            continue

        nuevas.add((f, c))

        if tablero[f][c] != 0:
            continue

        filas = len(tablero)
        columnas = len(tablero[0])

        for nf, nc in obtener_vecinas(
            f,
            c,
            filas,
            columnas
        ):

            if (nf, nc) in minas:
                continue

            if (nf, nc) not in nuevas:
                cola.append((nf, nc))

    return nuevas

def verificar_victoria(
    descubiertas,
    filas,
    columnas,
    cantidad_minas
):

    total_seguras = (
        filas * columnas
    ) - cantidad_minas

    return len(descubiertas) >= total_seguras

NIVELES = {
    "FACIL": {
        "filas": 8,
        "columnas": 8,
        "minas": 10,
        "tiempo": 240,
        "multiplicador": 1.0,
    },
    "NORMAL": {
        "filas": 10,
        "columnas": 10,
        "minas": 18,
        "tiempo": 360,
        "multiplicador": 1.5,
    },
    "DIFICIL": {
        "filas": 12,
        "columnas": 12,
        "minas": 30,
        "tiempo": 480,
        "multiplicador": 2.0,
    },
}

def es_mina(fila, columna, minas):
    """
    Determina si la casilla seleccionada contiene una mina.
    """
    return (fila, columna) in minas

def calcular_puntaje(
    segundos_restantes,
    multiplicador
):
    return int(
        (800 + (3 * segundos_restantes))
        * multiplicador
    )

def tiempo_agotado(
    duracion,
    limite
):
    return duracion >= limite

def cambiar_bandera(
    fila,
    columna,
    banderas
):
    """
    Coloca o quita una bandera.
    """

    posicion = (fila, columna)

    if posicion in banderas:
        banderas.remove(posicion)

    else:
        banderas.add(posicion)

    return banderas

def puede_descubrir(
    fila,
    columna,
    banderas
):
    """
    No permite descubrir una casilla
    que tenga bandera.
    """

    return (fila, columna) not in banderas