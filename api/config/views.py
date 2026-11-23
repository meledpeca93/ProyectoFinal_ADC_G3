from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe
from django.views.decorators.vary import vary_on_headers


@require_safe
@never_cache
@vary_on_headers("Accept", "X-Buscaminas-Proxy")
def salud(request):
    disponible = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        disponible = False

    codigo = 200 if disponible else 503
    if request.get_preferred_type(["application/json", "text/html"]) == "text/html":
        return render(
            request,
            "salud.html",
            {
                "disponible": disponible,
                "codigo": codigo,
                "proxy_verificado": request.headers.get("X-Buscaminas-Proxy") == "caddy",
            },
            status=codigo,
        )

    estado = "ok" if disponible else "no_disponible"
    return JsonResponse({"estado": estado}, status=codigo)
