from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import AccesoForm
from .views import registro

app_name = "cuentas"

pantalla_acceso = LoginView.as_view(
    template_name="cuentas/login.html",
    authentication_form=AccesoForm,
    redirect_authenticated_user=True,
)

urlpatterns = [
    path("registro/", registro, name="registro"),
    path("login/", pantalla_acceso, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
