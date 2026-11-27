from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .forms import PerfilForm, RegistroForm
from .models import PerfilJugador


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def registro(request):
    destino = request.POST.get("next") or request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        destino = ""
    if request.user.is_authenticated:
        return redirect(destino or "perfil")

    form = RegistroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            usuario = form.save()
            PerfilJugador.objects.create(user=usuario)
        login(request, usuario)
        return redirect(destino or "perfil")
    return render(request, "cuentas/registro.html", {"form": form, "next": destino})


@never_cache
@login_required
@require_http_methods(["GET", "HEAD", "POST"])
def perfil(request):
    preferencias, _ = PerfilJugador.objects.get_or_create(user=request.user)
    form = PerfilForm(
        request.POST if request.method == "POST" else None,
        instance=preferencias,
    )
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Tus preferencias se guardaron.")
            return redirect("perfil")
        preferencias.refresh_from_db()
    return render(request, "cuentas/perfil.html", {"form": form, "preferencias": preferencias})
