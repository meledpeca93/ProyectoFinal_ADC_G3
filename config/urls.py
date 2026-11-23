from django.urls import path
from django.views.generic import TemplateView

from .views import salud

urlpatterns = [
    path("", TemplateView.as_view(template_name="inicio_provisional.html")),
    path("salud/", salud, name="salud"),
]
