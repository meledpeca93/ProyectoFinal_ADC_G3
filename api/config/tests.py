from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase, TestCase


class SaludPostgreSQLTests(TestCase):
    def test_postgresql_disponible(self):
        respuesta = self.client.get("/salud/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {"estado": "ok"})

    def test_vista_navegador_operativa(self):
        respuesta = self.client.get("/salud/", headers={
            "Accept": "text/html,*/*;q=0.8",
            "X-Buscaminas-Proxy": "caddy",
        })
        self.assertContains(respuesta, "Operativo")
        self.assertContains(respuesta, "HTTP 200")
        self.assertContains(respuesta, ">Healthy</span>", count=3)
        self.assertIn("Accept", respuesta.headers["Vary"])
        self.assertIn("no-store", respuesta.headers["Cache-Control"])


class SaludHTTPTests(SimpleTestCase):
    @patch("config.views.connection")
    def test_postgresql_no_disponible(self, conexion):
        conexion.cursor.side_effect = OperationalError
        respuesta = self.client.get("/salud/")
        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(respuesta.json(), {"estado": "no_disponible"})

    @patch("config.views.connection")
    def test_vista_navegador_no_disponible(self, conexion):
        conexion.cursor.side_effect = OperationalError
        respuesta = self.client.get("/salud/", headers={
            "Accept": "text/html",
            "X-Buscaminas-Proxy": "caddy",
        })
        self.assertContains(respuesta, "No disponible", status_code=503)
        self.assertContains(respuesta, "HTTP 503", status_code=503)
        self.assertContains(respuesta, ">Healthy</span>", count=2, status_code=503)
        self.assertContains(respuesta, ">Unhealthy</span>", count=1, status_code=503)

    @patch("config.views.connection")
    def test_vista_directa_no_verifica_caddy(self, conexion):
        respuesta = self.client.get("/salud/", headers={"Accept": "text/html"})
        self.assertContains(respuesta, "Sin verificar")

    @patch("config.views.connection")
    def test_accept_generico_conserva_json(self, conexion):
        respuesta = self.client.get("/salud/", headers={"Accept": "*/*"})
        self.assertEqual(respuesta.json(), {"estado": "ok"})
        conexion.cursor.return_value.__enter__.return_value.execute.assert_called_once_with("SELECT 1")

    def test_solo_lectura(self):
        self.assertEqual(self.client.post("/salud/").status_code, 405)
