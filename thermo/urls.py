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

    path("materiaux/", views.materiaux_hub, name="materiaux_hub"),

    path("materiaux/categories/nouveau/", views.categorie_batiment_creer, name="categorie_batiment_creer"),
    path("materiaux/categories/<int:pk>/modifier/", views.categorie_batiment_modifier, name="categorie_batiment_modifier"),
    path("materiaux/categories/<int:pk>/supprimer/", views.categorie_batiment_supprimer, name="categorie_batiment_supprimer"),

    path("materiaux/planchers/nouveau/", views.materiau_plancher_creer, name="materiau_plancher_creer"),
    path("materiaux/planchers/<int:pk>/modifier/", views.materiau_plancher_modifier, name="materiau_plancher_modifier"),
    path("materiaux/planchers/<int:pk>/supprimer/", views.materiau_plancher_supprimer, name="materiau_plancher_supprimer"),

    path("materiaux/murs/nouveau/", views.materiau_mur_creer, name="materiau_mur_creer"),
    path("materiaux/murs/<int:pk>/modifier/", views.materiau_mur_modifier, name="materiau_mur_modifier"),
    path("materiaux/murs/<int:pk>/supprimer/", views.materiau_mur_supprimer, name="materiau_mur_supprimer"),

    path("materiaux/toitures/nouveau/", views.materiau_toiture_creer, name="materiau_toiture_creer"),
    path("materiaux/toitures/<int:pk>/modifier/", views.materiau_toiture_modifier, name="materiau_toiture_modifier"),
    path("materiaux/toitures/<int:pk>/supprimer/", views.materiau_toiture_supprimer, name="materiau_toiture_supprimer"),

    path("materiaux/ouvrants/nouveau/", views.materiau_ouvrant_creer, name="materiau_ouvrant_creer"),
    path("materiaux/ouvrants/<int:pk>/modifier/", views.materiau_ouvrant_modifier, name="materiau_ouvrant_modifier"),
    path("materiaux/ouvrants/<int:pk>/supprimer/", views.materiau_ouvrant_supprimer, name="materiau_ouvrant_supprimer"),
]
