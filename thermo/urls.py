from django.urls import path

from . import views

app_name = "thermo"

urlpatterns = [
    path("", views.tableau_de_bord, name="tableau_de_bord"),
    path("batiments/", views.batiment_liste, name="batiment_liste"),
    path("batiments/nouveau/", views.batiment_creer, name="batiment_creer"),
    path("batiments/<int:pk>/", views.batiment_detail, name="batiment_detail"),
    path("batiments/<int:pk>/modifier/", views.batiment_modifier, name="batiment_modifier"),
    path("batiments/<int:pk>/supprimer/", views.batiment_supprimer, name="batiment_supprimer"),
]
