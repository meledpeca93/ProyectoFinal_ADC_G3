from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import PerfilJugador


User = get_user_model()


class RegistroTests(TestCase):
    def setUp(self):
        self.url = reverse("cuentas:registro")
        self.datos = {
            "username": "jugar01",
            "email": "jugador@example.com",
            "password1": "Cascada-Azul-42!",
            "password2": "Cascada-Azul-42!",
        }

    def test_registro_crea_perfil_y_abre_sesion(self):
        self.assertRedirects(self.client.post(self.url, self.datos), reverse("perfil"))
        usuario = User.objects.get(username="jugar01")
        self.assertTrue(usuario.check_password(self.datos["password1"]))
        self.assertTrue(PerfilJugador.objects.filter(user=usuario).exists())
        self.assertEqual(str(usuario.pk), self.client.session["_auth_user_id"])

    def test_rechaza_correo_invalido_y_contrasena_debil(self):
        self.datos.update(email="sin-arroba", password1="1234", password2="1234")
        respuesta = self.client.post(self.url, self.datos)
        self.assertIn("email", respuesta.context["form"].errors)
        self.assertIn("password2", respuesta.context["form"].errors)
        self.assertFalse(User.objects.exists())

    def test_rechaza_usuario_duplicado(self):
        User.objects.create_user(username="jugar01")
        respuesta = self.client.post(self.url, self.datos)
        self.assertIn("username", respuesta.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)


class SesionPerfilTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user("jugador", password="Cascada-Azul-42!")
        cls.otro = PerfilJugador.objects.create(user=User.objects.create_user("otro"), alias="Privado")

    def test_perfil_requiere_sesion(self):
        self.assertRedirects(self.client.get(reverse("perfil")), "/cuentas/login/?next=/perfil/")

    def test_login_por_correo_y_error_con_clave_invalida(self):
        self.usuario.email = "jugador@example.com"
        self.usuario.save(update_fields=["email"])
        url = reverse("cuentas:login")
        datos = {"username": "JUGADOR@example.com", "password": "incorrecta"}
        respuesta = self.client.post(url, datos)
        self.assertEqual(respuesta.context["form"].non_field_errors().as_data()[0].code, "invalid_login")
        self.assertNotIn("_auth_user_id", self.client.session)
        datos["password"] = "Cascada-Azul-42!"
        self.assertRedirects(self.client.post(url, datos), reverse("perfil"))

    def test_portada_muestra_acceso_y_permite_iniciar_sesion(self):
        inicio = reverse("inicio")
        respuesta = self.client.get(inicio)
        self.assertContains(respuesta, "titulo-acceso")
        self.assertContains(respuesta, reverse("cuentas:registro"))
        self.assertRedirects(self.client.post(inicio, {
            "username": "jugador",
            "password": "Cascada-Azul-42!",
        }), reverse("perfil"))
        self.assertRedirects(self.client.get(inicio), reverse("perfil"))

    def test_login_y_logout_solo_post_con_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        login_url = reverse("cuentas:login")
        cliente.get(login_url)
        token = cliente.cookies["csrftoken"].value
        self.assertRedirects(cliente.post(login_url, {
            "username": "jugador",
            "password": "Cascada-Azul-42!",
            "csrfmiddlewaretoken": token,
            "next": "https://example.com",
        }), reverse("perfil"))
        logout_url = reverse("cuentas:logout")
        self.assertEqual(cliente.get(logout_url).status_code, 405)
        self.assertEqual(cliente.post(logout_url).status_code, 403)
        token = cliente.cookies["csrftoken"].value
        self.assertRedirects(
            cliente.post(logout_url, {"csrfmiddlewaretoken": token}),
            login_url,
        )
        self.assertNotIn("_auth_user_id", cliente.session)

    def test_edita_preferencias_del_usuario_autenticado(self):
        self.client.force_login(self.usuario)
        url = reverse("perfil")
        self.assertNotContains(self.client.get(url), "Privado")
        respuesta = self.client.post(url, {
            "alias": "Neón",
            "volumen_musica": 0,
            "volumen_efectos": 100,
            "silenciado": "on",
            "user": self.otro.user_id,
        })
        self.assertRedirects(respuesta, url)
        perfil = PerfilJugador.objects.get(user=self.usuario)
        self.assertEqual((perfil.alias, perfil.volumen_musica, perfil.volumen_efectos), ("Neón", 0, 100))
        self.assertTrue(perfil.silenciado)
        self.otro.refresh_from_db()
        self.assertEqual(self.otro.alias, "Privado")
        self.assertContains(self.client.get(url), "Neón")

    def test_rechaza_volumenes_fuera_de_rango(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse("perfil"), {
            "volumen_musica": -1,
            "volumen_efectos": 101,
        })
        self.assertIn("volumen_musica", respuesta.context["form"].errors)
        self.assertIn("volumen_efectos", respuesta.context["form"].errors)
        self.assertEqual(PerfilJugador.objects.get(user=self.usuario).volumen_efectos, 50)
