import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="PerfilJugador",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("alias", models.CharField(blank=True, max_length=50)),
                ("volumen_musica", models.PositiveSmallIntegerField(default=50, validators=[django.core.validators.MaxValueValidator(100)])),
                ("volumen_efectos", models.PositiveSmallIntegerField(default=50, validators=[django.core.validators.MaxValueValidator(100)])),
                ("silenciado", models.BooleanField(default=False)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="perfil_jugador", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="perfiljugador",
            constraint=models.CheckConstraint(
                condition=models.Q(volumen_musica__lte=100, volumen_efectos__lte=100),
                name="cuentas_volumen_maximo_100",
            ),
        ),
    ]
