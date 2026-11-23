from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField

from .models import PerfilJugador


class AccesoForm(AuthenticationForm):
    username = UsernameField(
        label="Usuario o correo",
        max_length=254,
        widget=forms.TextInput(attrs={
            "autofocus": True,
            "autocomplete": "username",
            "placeholder": "Ingresa tu usuario o correo",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campo = self.fields["username"]
        campo.widget.attrs["maxlength"] = campo.max_length

    def clean(self):
        identificador = self.cleaned_data.get("username")
        if identificador and "@" in identificador:
            usuarios = self._usuarios_por_correo(identificador)
            if len(usuarios) == 1:
                self.cleaned_data["username"] = usuarios[0]
        return super().clean()

    def _usuarios_por_correo(self, identificador):
        usuarios = get_user_model()._default_manager
        if usuarios.filter(username=identificador).exists():
            return []
        return list(usuarios.filter(email__iexact=identificador).values_list("username", flat=True)[:2])


class RegistroForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput(attrs={
        "autocomplete": "email",
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.help_text = ""

    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")


class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilJugador
        fields = ("alias", "volumen_musica", "volumen_efectos", "silenciado")
        labels = {
            "volumen_musica": "Volumen de música (%)",
            "volumen_efectos": "Volumen de efectos (%)",
            "silenciado": "Silenciar todo",
        }

        widgets = {
            "volumen_musica": forms.NumberInput(attrs={"type": "range", "min": 0, "max": 100}),
            "volumen_efectos": forms.NumberInput(attrs={"type": "range", "min": 0, "max": 100}),
        }
