import uuid

from django.conf import settings
from django.db import models


class Partida(models.Model):

    ESTADOS = [
        ("EN_CURSO", "En curso"),
        ("GANADA", "Ganada"),
        ("PERDIDA", "Perdida"),
        ("TIEMPO_AGOTADO", "Tiempo agotado"),
        ("ABANDONADA", "Abandonada"),
    ]

    DIFICULTADES = [
        ("FACIL", "Facil"),
        ("NORMAL", "Normal"),
        ("DIFICIL", "Dificil"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="partidas"
    )

    dificultad = models.CharField(
        max_length=20,
        choices=DIFICULTADES
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="EN_CURSO"
    )

    inicio_servidor = models.DateTimeField(auto_now_add=True)

    fin_servidor = models.DateTimeField(
        null=True,
        blank=True
    )

    limite_segundos = models.PositiveIntegerField()

    duracion_segundos = models.PositiveIntegerField(
        default=0
    )

    puntaje = models.PositiveIntegerField(
        default=0
    )

    movimientos = models.PositiveIntegerField(
        default=0
    )

    estado_juego = models.JSONField(
        default=dict
    )

    def __str__(self):
        return f"{self.usuario} - {self.dificultad}"

class Movimiento(models.Model):

    TIPOS = [
        ("DESCUBRIR", "Descubrir"),
        ("BANDERA", "Bandera"),
    ]

    partida = models.ForeignKey(
        Partida,
        on_delete=models.CASCADE,
        related_name="registro_movimientos"
    )

    numero = models.PositiveIntegerField()

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    datos = models.JSONField(
        default=dict
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    aceptado = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = (
            "partida",
            "numero",
        )