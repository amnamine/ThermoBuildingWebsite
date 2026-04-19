from django.contrib import admin

from .models import Batiment, CategorieBatiment, TypeMur, TypeOuvrant, TypePlancher, TypeToiture


@admin.register(TypePlancher, TypeMur, TypeToiture, TypeOuvrant)
class TypeCoefficientAdmin(admin.ModelAdmin):
    list_display = ("nom", "k", "actif")
    list_filter = ("actif",)
    search_fields = ("nom",)
    ordering = ("nom",)


@admin.register(Batiment)
class BatimentAdmin(admin.ModelAdmin):
    list_display = ("nom", "categorie", "classe", "consommation", "cree_le")
    search_fields = ("nom", "description")
    list_select_related = ("categorie", "type_plancher", "type_mur", "type_toiture", "type_ouvrant")
    date_hierarchy = "cree_le"

    @admin.display(description="Classe")
    def classe(self, obj: Batiment) -> str:
        return obj.classe_energie

    @admin.display(description="Conso (kWh/m²/an)")
    def consommation(self, obj: Batiment) -> str:
        return f"{obj.consommation_kwh_m2_an:.2f}"


@admin.register(CategorieBatiment)
class CategorieBatimentAdmin(admin.ModelAdmin):
    list_display = ("nom", "actif")
    list_filter = ("actif",)
    search_fields = ("nom",)
