from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from juego.models import Partida
from juego.services.minas import es_mina
from juego.services.minas import (
    generar_minas,
    obtener_vecinas,
    construir_tablero,
    verificar_victoria,
    descubrir_cascada,
    calcular_puntaje,
    tiempo_agotado,
    cambiar_bandera, puede_descubrir
)


class MinasTests(TestCase):

    def test_primer_click_seguro(self):

        filas = 8
        columnas = 8
        cantidad_minas = 10

        for _ in range(1000):

            fila = 3
            columna = 4

            minas = generar_minas(
                filas,
                columnas,
                cantidad_minas,
                (fila, columna)
            )

            self.assertEqual(
                len(minas),
                cantidad_minas
            )

            self.assertNotIn(
                (fila, columna),
                minas
            )

            for vecina in obtener_vecinas(
                fila,
                columna,
                filas,
                columnas
            ):
                self.assertNotIn(
                    vecina,
                    minas
                )

def test_cantidad_exacta_minas(self):

    minas = generar_minas(
        filas=8,
        columnas=8,
        cantidad_minas=10,
        primer_click=(3, 4)
    )

    self.assertEqual(
        len(minas),
        10
    )

from juego.services.minas import (
    generar_minas,
    obtener_vecinas,
    construir_tablero,
)

def test_construccion_tablero(self):

    minas = {
        (0, 0)
    }

    tablero = construir_tablero(
        3,
        3,
        minas
    )

    self.assertEqual(
        tablero[0][0],
        -1
    )

    self.assertEqual(
        tablero[0][1],
        1
    )

def test_verificar_victoria(self):

    descubiertas = set()

    for f in range(8):
        for c in range(8):

            if len(descubiertas) < 54:
                descubiertas.add((f, c))

    self.assertTrue(
        verificar_victoria(
            descubiertas,
            8,
            8,
            10
        )
    )

def test_bfs_expansion(self):

    minas = {
        (0, 0)
    }

    tablero = construir_tablero(
        5,
        5,
        minas
    )

    resultado = descubrir_cascada(
        4,
        4,
        tablero,
        set(),
        minas
    )

    self.assertTrue(
        len(resultado) > 1
    ) 


def test_derrota_por_mina(self):

    minas = {
        (2, 3)
    }

    self.assertTrue(
        es_mina(
            2,
            3,
            minas
        )
    )

    self.assertFalse(
        es_mina(
            0,
            0,
            minas
        )
    )   
def test_calculo_puntaje(self):

    puntaje = calcular_puntaje(
        100,
        1.5
    )

    self.assertEqual(
        puntaje,
        1650
    )

def test_tiempo_agotado(self):

    self.assertTrue(
        tiempo_agotado(
            240,
            240
        )
    )

    self.assertFalse(
        tiempo_agotado(
            100,
            240
        )
    )

def test_colocar_bandera(self):

    banderas = set()

    resultado = cambiar_bandera(
        2,
        3,
        banderas
    )

    self.assertIn(
        (2, 3),
        resultado
    )

def test_quitar_bandera(self):

    banderas = {
        (2, 3)
    }

    resultado = cambiar_bandera(
        2,
        3,
        banderas
    )

    self.assertNotIn(
        (2, 3),
        resultado
    )   

def test_endpoint_nueva_partida(self):

    client = Client()

    respuesta = client.post(
        "/inicio-juego/partidas/nueva/"
    )

    self.assertEqual(
        respuesta.status_code,
        200
    )

def test_no_descubrir_con_bandera(self):

    banderas = {
        (2, 3)
    }

    self.assertFalse(
        puede_descubrir(
            2,
            3,
            banderas
        )
    )

    self.assertTrue(
        puede_descubrir(
            0,
            0,
            banderas
        )
    )

def test_crear_partida(self):

    usuario = User.objects.create_user(
        username="prueba",
        password="123456"
    )

    partida = Partida.objects.create(
        usuario=usuario,
        dificultad="FACIL",
        limite_segundos=240,
        estado_juego={}
    )

    self.assertEqual(
        partida.estado,
        "EN_CURSO"
    )

def test_consulta_partida(self):

    usuario = User.objects.create_user(
        username="consulta",
        password="123456"
    )

    partida = Partida.objects.create(
        usuario=usuario,
        dificultad="FACIL",
        limite_segundos=240,
        estado_juego={}
    )

    self.assertEqual(
        partida.dificultad,
        "FACIL"
    )

def test_cambiar_bandera(self):

    banderas = set()

    resultado = cambiar_bandera(
        1,
        1,
        banderas
    )

    self.assertIn(
        (1, 1),
        resultado
    )   

def test_descubrir_casilla(self):

    descubiertas = set()

    descubiertas.add(
        (1, 1)
    )

    self.assertIn(
        (1, 1),
        descubiertas
    )    
