from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from cuentas.models import PerfilJugador
from juego.models import Partida
from juego.views import NIVELES_CONFIG, calcular_puntaje_oficial

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


class InicioTests(TestCase):
    def setUp(self):
        self.url = reverse("inicio")

    def test_inicio_visitante_muestra_componentes_y_accesos_reales(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "juego/inicio.html")
        self.assertContains(respuesta, "Juego educativo")
        self.assertContains(respuesta, "¡Bienvenido a Buscaminas!")
        self.assertContains(respuesta, "Jugar ahora")
        self.assertContains(respuesta, reverse("cuentas:login"))
        self.assertContains(respuesta, reverse("cuentas:registro"))
        self.assertContains(respuesta, "Características")
        self.assertContains(respuesta, "Python · Django · PostgreSQL · Docker")
        for datos in NIVELES_CONFIG.values():
            self.assertContains(respuesta, datos["nombre"])
            self.assertContains(respuesta, f'{datos["minas"]} minas')
        self.assertNotContains(respuesta, "💣")
        self.assertNotContains(respuesta, "🏆")
        self.assertNotContains(respuesta, "http://127.0.0.1")

    def test_inicio_autenticado_adapta_sesion_sin_registro(self):
        usuario = User.objects.create_user("hero01", password="Clave-Segura-123!")
        PerfilJugador.objects.create(user=usuario, alias="NeonHero")
        self.client.force_login(usuario)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "NeonHero")
        self.assertContains(respuesta, reverse("perfil"))
        self.assertContains(respuesta, reverse("cuentas:logout"))
        self.assertNotContains(respuesta, "Registrarse")
        self.assertEqual(respuesta.context["dificultad_seleccionada"], "normal")

        personalizado = self.client.get(self.url, {"nivel": "dificil"})
        self.assertEqual(personalizado.context["dificultad_seleccionada"], "dificil")


class ResultadoDemoTests(TestCase):
    def setUp(self):
        self.url = reverse("resultado_demo")

    def test_desenlaces_responden_ok_sin_emojis_ni_localhost(self):
        for estado, texto_esperado in (
            ("GANADA", "¡Partida ganada!"),
            ("PERDIDA", "¡Partida perdida!"),
            ("TIEMPO_AGOTADO", "Tiempo agotado"),
            ("ABANDONADA", "Partida abandonada"),
        ):
            respuesta = self.client.get(self.url, {"estado": estado})
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, texto_esperado)
            self.assertNotContains(respuesta, "🏆")
            self.assertNotContains(respuesta, "💣")
            self.assertNotContains(respuesta, "http://127.0.0.1")
            self.assertNotContains(respuesta, "http://localhost")

    def test_consistencia_tablero_y_metricas_por_nivel(self):
        casos = (
            ("facil", "Fácil", 8, 10, 54),
            ("normal", "Normal", 10, 18, 82),
            ("dificil", "Difícil", 12, 30, 114),
        )
        for nivel, nombre, lado, minas, seguras in casos:
            respuesta = self.client.get(self.url, {"estado": "GANADA", "nivel": nivel})
            self.assertEqual(respuesta.status_code, 200)
            ctx = respuesta.context
            self.assertEqual(ctx["nivel_nombre"], nombre)
            self.assertEqual(ctx["filas"], lado)
            self.assertEqual(ctx["columnas"], lado)
            self.assertEqual(ctx["minas_total"], minas)
            self.assertEqual(ctx["seguras_descubiertas"], seguras)
            self.assertEqual(ctx["seguras_total"], seguras)
            self.assertEqual(ctx["banderas"], minas)
            celdas = [celda for fila in ctx["tablero_matriz"] for celda in fila]
            self.assertEqual(len(celdas), lado * lado)
            self.assertEqual(sum(1 for c in celdas if c["tipo"] == "descubierta"), seguras)
            self.assertEqual(sum(1 for c in celdas if c["tipo"] == "bandera"), minas)

    def test_puntaje_oficial_y_logros_segun_desenlace(self):
        ganada_normal = self.client.get(self.url, {"estado": "GANADA", "nivel": "normal"})
        self.assertEqual(
            ganada_normal.context["puntaje_final"],
            calcular_puntaje_oficial("GANADA", "normal", ganada_normal.context["duracion_segundos"]),
        )
        self.assertEqual(ganada_normal.context["logros_obtenidos"], 3)
        self.assertContains(ganada_normal, "¡Nuevo mejor puntaje personal!")

        ganada_facil = self.client.get(self.url, {"estado": "GANADA", "nivel": "facil"})
        self.assertEqual(ganada_facil.context["logros_obtenidos"], 2)

        sin_record = self.client.get(self.url, {"estado": "GANADA", "nivel": "normal", "record": "0"})
        self.assertFalse(sin_record.context["comparativa"]["es_nuevo_record"])
        self.assertNotContains(sin_record, "¡Nuevo mejor puntaje personal!")

        for estado in ("PERDIDA", "TIEMPO_AGOTADO", "ABANDONADA"):
            derrota = self.client.get(self.url, {"estado": estado, "nivel": "normal"})
            self.assertEqual(derrota.context["puntaje_final"], 0)
            self.assertEqual(derrota.context["logros_obtenidos"], 0)
            self.assertFalse(derrota.context["comparativa"]["es_nuevo_record"])
            self.assertNotContains(derrota, "¡Nuevo mejor puntaje personal!")

    def test_usuario_autenticado_con_y_sin_perfil(self):
        usuario_con_perfil = User.objects.create_user("jugador01", password="Clave-Segura-123!")
        PerfilJugador.objects.create(user=usuario_con_perfil, alias="NeonPro")
        self.client.force_login(usuario_con_perfil)
        resp = self.client.get(self.url)
        self.assertContains(resp, "NeonPro")
        self.assertContains(resp, reverse("cuentas:logout"))

        usuario_sin_perfil = User.objects.create_user("jugador02", password="Clave-Segura-123!")
        self.client.force_login(usuario_sin_perfil)
        resp_sin_perfil = self.client.get(self.url)
        self.assertEqual(resp_sin_perfil.status_code, 200)
        self.assertContains(resp_sin_perfil, "jugador02")


class ResultadoPartidaTests(TestCase):
    def test_abandono_enlaza_resultado_persistido_y_privado(self):
        propietario = User.objects.create_user("dueño")
        self.client.force_login(propietario)
        creada = self.client.post(reverse("nueva_partida"), {"nivel": "NORMAL"}, content_type="application/json")
        self.assertEqual(creada.status_code, 200)
        identificador = creada.json()["partida_id"]
        resultado = reverse("resultado_partida", args=[identificador])
        self.assertEqual(self.client.get(resultado).status_code, 404)

        abandono = self.client.post(reverse("abandonar_partida", args=[identificador]))
        self.assertEqual(abandono.json()["resultado_url"], resultado)
        respuesta = self.client.get(resultado)
        self.assertContains(respuesta, "Partida abandonada")
        self.assertEqual(respuesta.context["puntaje_final"], 0)
        self.assertEqual(len(respuesta.context["tablero_matriz"]), 10)
        self.assertEqual(respuesta.context["seguras_descubiertas"], 0)

        self.client.force_login(User.objects.create_user("otro-jugador"))
        self.assertEqual(self.client.get(resultado).status_code, 404)
