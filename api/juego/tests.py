from django.test import TestCase, Client
from django.contrib.auth.models import User
from juego.models import Partida

from juego.services.minas import (
    generar_minas,
    obtener_vecinas,
    construir_tablero,
    verificar_victoria,
    descubrir_cascada,
    calcular_puntaje,
    tiempo_agotado,
    cambiar_bandera,
    puede_descubrir,
    es_mina
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
                filas, columnas, cantidad_minas,
                (fila, columna)
            )

            self.assertEqual(len(minas), cantidad_minas)
            self.assertNotIn((fila, columna), minas)

            for vecina in obtener_vecinas(
                fila, columna, filas, columnas
            ):
                self.assertNotIn(vecina, minas)

    def test_cantidad_exacta_minas(self):

        minas = generar_minas(
            filas=8,
            columnas=8,
            cantidad_minas=10,
            primer_click=(3, 4)
        )

        self.assertEqual(len(minas), 10)

    def test_construccion_tablero(self):

        minas = {(0, 0)}

        tablero = construir_tablero(3, 3, minas)

        self.assertEqual(tablero[0][0], -1)
        self.assertEqual(tablero[0][1], 1)

    def test_verificar_victoria(self):

        descubiertas = set()

        for f in range(8):
            for c in range(8):
                if len(descubiertas) < 54:
                    descubiertas.add((f, c))

        self.assertTrue(
            verificar_victoria(descubiertas, 8, 8, 10)
        )

    def test_bfs_expansion(self):

        minas = {(0, 0)}

        tablero = construir_tablero(5, 5, minas)

        resultado = descubrir_cascada(
            4, 4, tablero, set(), minas
        )

        self.assertTrue(len(resultado) > 1)

    def test_derrota_por_mina(self):

        minas = {(2, 3)}

        self.assertTrue(es_mina(2, 3, minas))
        self.assertFalse(es_mina(0, 0, minas))

    def test_calculo_puntaje(self):

        puntaje = calcular_puntaje(100, 1.5)

        self.assertEqual(puntaje, 1650)

    def test_tiempo_agotado(self):

        self.assertTrue(tiempo_agotado(240, 240))
        self.assertFalse(tiempo_agotado(100, 240))

    def test_colocar_bandera(self):

        banderas = set()

        resultado = cambiar_bandera(2, 3, banderas)

        self.assertIn((2, 3), resultado)

    def test_quitar_bandera(self):

        banderas = {(2, 3)}

        resultado = cambiar_bandera(2, 3, banderas)

        self.assertNotIn((2, 3), resultado)

    def test_endpoint_nueva_partida(self):

        usuario = User.objects.create_user(
            username="prueba",
            password="123456"
        )

        client = Client()
        client.force_login(usuario)

        respuesta = client.post(
            "/inicio-juego/partidas/nueva/",
            '{"nivel": "FACIL"}',
            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, 200)

    def test_no_descubrir_con_bandera(self):

        banderas = {(2, 3)}

        self.assertFalse(
            puede_descubrir(2, 3, banderas)
        )

        self.assertTrue(
            puede_descubrir(0, 0, banderas)
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

        self.assertEqual(partida.estado, "EN_CURSO")

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

        self.assertEqual(partida.dificultad, "FACIL")

    def test_cambiar_bandera(self):

        banderas = set()

        resultado = cambiar_bandera(1, 1, banderas)

        self.assertIn((1, 1), resultado)

    def test_descubrir_casilla(self):

        minas = {(0, 0)}

        tablero = construir_tablero(3, 3, minas)

        resultado = descubrir_cascada(
            1, 1, tablero, set(), minas
        )

        self.assertIn((1, 1), resultado)
        self.assertNotIn((0, 0), resultado)

    def test_movimiento_repetido(self):

        usuario = User.objects.create_user(
            username="repetido",
            password="123456"
        )

        self.client.force_login(usuario)

        respuesta = self.client.post(
            "/inicio-juego/partidas/nueva/",
            '{"nivel": "FACIL"}',
            content_type="application/json"
        )

        partida_id = respuesta.json()["partida_id"]

        url = f"/inicio-juego/api/partidas/{partida_id}/accion/"

        datos = '{"numero": 1, "tipo": "DESCUBRIR", "f": 3, "c": 4}'

        primera = self.client.post(
            url, datos,
            content_type="application/json"
        )

        segunda = self.client.post(
            url, datos,
            content_type="application/json"
        )

        self.assertEqual(primera.status_code, 200)
        self.assertEqual(segunda.status_code, 200)

        self.assertEqual(primera.json(), segunda.json())

        partida = Partida.objects.get(id=partida_id)

        self.assertEqual(partida.movimientos, 1)

    def test_partida_ajena(self):

        usuario = User.objects.create_user(
            username="propietario",
            password="123456"
        )

        otro = User.objects.create_user(
            username="visitante",
            password="123456"
        )

        partida = Partida.objects.create(
            usuario=usuario,
            dificultad="FACIL",
            limite_segundos=240,
            estado_juego={}
        )

        self.client.force_login(otro)

        respuesta = self.client.get(
            f"/inicio-juego/api/partidas/{partida.id}/estado/"
        )

        self.assertEqual(respuesta.status_code, 404)

    def test_movimiento_partida_finalizada(self):

        usuario = User.objects.create_user(
            username="finalizada",
            password="123456"
        )

        self.client.force_login(usuario)

        respuesta = self.client.post(
            "/inicio-juego/partidas/nueva/",
            '{"nivel": "FACIL"}',
            content_type="application/json"
        )

        partida_id = respuesta.json()["partida_id"]

        self.client.post(
            f"/inicio-juego/api/partidas/{partida_id}/abandonar/"
        )

        respuesta = self.client.post(
            f"/inicio-juego/api/partidas/{partida_id}/accion/",
            '{"numero": 1, "tipo": "DESCUBRIR", "f": 3, "c": 4}',
            content_type="application/json"
        )

        self.assertEqual(respuesta.status_code, 409)

        partida = Partida.objects.get(id=partida_id)

        self.assertEqual(partida.estado, "ABANDONADA")
        self.assertEqual(partida.movimientos, 0)