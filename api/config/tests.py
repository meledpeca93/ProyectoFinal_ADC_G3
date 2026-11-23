from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase, TestCase


class SaludPostgreSQLTests(TestCase):
    def test_postgresql_disponible(self):
        respuesta = self.client.get("/salud/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {"estado": "ok"})

class SaludHTTPTests(SimpleTestCase):
    @patch("config.views.connection")
    def test_postgresql_no_disponible(self, conexion):
        conexion.cursor.side_effect = OperationalError
        respuesta = self.client.get("/salud/")
        self.assertEqual(respuesta.status_code, 503)
        self.assertEqual(respuesta.json(), {"estado": "no_disponible"})

    def test_solo_lectura(self):
        self.assertEqual(self.client.post("/salud/").status_code, 405)
