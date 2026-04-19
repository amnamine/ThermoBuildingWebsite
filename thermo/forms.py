from __future__ import annotations

from django import forms

from .models import (
    Batiment,
    CategorieBatiment,
    TypeMur,
    TypeOuvrant,
    TypePlancher,
    TypeToiture,
)


class BatimentForm(forms.ModelForm):
    class Meta:
        model = Batiment
        fields = [
            "nom",
            "categorie",
            "description",
            "surface_habitable_m2",
            "type_plancher",
            "surface_plancher_m2",
            "type_mur",
            "surface_mur_m2",
            "type_toiture",
            "surface_toiture_m2",
            "type_ouvrant",
            "surface_ouvrants_m2",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-control")

        self.fields["categorie"].queryset = CategorieBatiment.objects.filter(actif=True)
        self.fields["type_plancher"].queryset = self.fields["type_plancher"].queryset.filter(actif=True)
        self.fields["type_mur"].queryset = self.fields["type_mur"].queryset.filter(actif=True)
        self.fields["type_toiture"].queryset = self.fields["type_toiture"].queryset.filter(actif=True)
        self.fields["type_ouvrant"].queryset = self.fields["type_ouvrant"].queryset.filter(actif=True)


class TypePlancherForm(forms.ModelForm):
    class Meta:
        model = TypePlancher
        fields = ["nom", "k", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "actif":
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class TypeMurForm(forms.ModelForm):
    class Meta:
        model = TypeMur
        fields = ["nom", "k", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "actif":
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class TypeToitureForm(forms.ModelForm):
    class Meta:
        model = TypeToiture
        fields = ["nom", "k", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "actif":
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class TypeOuvrantForm(forms.ModelForm):
    class Meta:
        model = TypeOuvrant
        fields = ["nom", "k", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "actif":
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class CategorieBatimentForm(forms.ModelForm):
    class Meta:
        model = CategorieBatiment
        fields = ["nom", "actif"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "actif":
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")
