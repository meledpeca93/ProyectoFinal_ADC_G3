from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models


class PerfilJugador(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_jugador",
    )
    alias = models.CharField(max_length=50, blank=True)
    volumen_musica = models.PositiveSmallIntegerField(default=50, validators=[MaxValueValidator(100)])
    volumen_efectos = models.PositiveSmallIntegerField(default=50, validators=[MaxValueValidator(100)])
    silenciado = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(volumen_musica__lte=100, volumen_efectos__lte=100),
                name="cuentas_volumen_maximo_100",
            ),
        ]
