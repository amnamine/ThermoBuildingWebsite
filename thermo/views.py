from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError, models
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    BatimentForm,
    CategorieBatimentForm,
    TypeMurForm,
    TypeOuvrantForm,
    TypePlancherForm,
    TypeToitureForm,
)
from .models import (
    Batiment,
    CategorieBatiment,
    TypeMur,
    TypeOuvrant,
    TypePlancher,
    TypeToiture,
)


@login_required
def tableau_de_bord(request: HttpRequest) -> HttpResponse:
    batiments = Batiment.objects.select_related("categorie").all()[:6]
    total = Batiment.objects.count()
    return render(
        request,
        "thermo/tableau_de_bord.html",
        {"batiments": batiments, "total": total},
    )


@login_required
def batiment_liste(request: HttpRequest) -> HttpResponse:
    qs = Batiment.objects.select_related(
        "categorie",
        "type_plancher",
        "type_mur",
        "type_toiture",
        "type_ouvrant",
    ).all()

    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(nom__icontains=q) | Q(description__icontains=q))

    categorie_id = request.GET.get("categorie")
    if categorie_id:
        if categorie_id.isdigit():
            qs = qs.filter(categorie_id=int(categorie_id))

    tri = request.GET.get("tri") or "cree_desc"
    classe = (request.GET.get("classe") or "").strip().upper()

    batiments = list(qs)
    for b in batiments:
        b._classe = b.classe_energie  # type: ignore[attr-defined]
        b._conso = b.consommation_kwh_m2_an  # type: ignore[attr-defined]
        b._deperd = b.deperdition_totale  # type: ignore[attr-defined]

    if classe and classe in {"A", "B", "C", "D", "E", "F", "G"}:
        batiments = [b for b in batiments if b._classe == classe]  # type: ignore[attr-defined]

    reverse = False
    if tri.endswith("_desc"):
        reverse = True
        tri_key = tri.removesuffix("_desc")
    elif tri.endswith("_asc"):
        tri_key = tri.removesuffix("_asc")
    else:
        tri_key = tri

    if tri_key == "nom":
        batiments.sort(key=lambda b: b.nom.lower(), reverse=reverse)
    elif tri_key == "conso":
        batiments.sort(key=lambda b: b._conso, reverse=reverse)  # type: ignore[attr-defined]
    elif tri_key == "deperd":
        batiments.sort(key=lambda b: b._deperd, reverse=reverse)  # type: ignore[attr-defined]
    elif tri_key == "classe":
        ordre = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6}
        batiments.sort(key=lambda b: ordre.get(b._classe, 99), reverse=reverse)  # type: ignore[attr-defined]
    else:  # cree
        batiments.sort(key=lambda b: b.cree_le, reverse=reverse)

    paginator = Paginator(batiments, 12)
    page = request.GET.get("page")
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    categories = CategorieBatiment.objects.filter(actif=True).order_by("nom")

    return render(
        request,
        "thermo/batiment_liste.html",
        {
            "page_obj": page_obj,
            "q": q,
            "tri": tri,
            "classe": classe,
            "categorie_id": categorie_id or "",
            "categories": categories,
        },
    )


@login_required
def batiment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    batiment = get_object_or_404(
        Batiment.objects.select_related(
            "categorie",
            "type_plancher",
            "type_mur",
            "type_toiture",
            "type_ouvrant",
        ),
        pk=pk,
    )
    return render(request, "thermo/batiment_detail.html", {"batiment": batiment})


@login_required
def batiment_creer(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BatimentForm(request.POST)
        if form.is_valid():
            batiment = form.save()
            messages.success(request, "Bâtiment créé avec succès.")
            return redirect("thermo:batiment_detail", pk=batiment.pk)
    else:
        form = BatimentForm()
    return render(request, "thermo/batiment_form.html", {"form": form, "mode": "creation"})


@login_required
def batiment_modifier(request: HttpRequest, pk: int) -> HttpResponse:
    batiment = get_object_or_404(Batiment, pk=pk)
    if request.method == "POST":
        form = BatimentForm(request.POST, instance=batiment)
        if form.is_valid():
            form.save()
            messages.success(request, "Modifications enregistrées.")
            return redirect("thermo:batiment_detail", pk=batiment.pk)
    else:
        form = BatimentForm(instance=batiment)
    return render(request, "thermo/batiment_form.html", {"form": form, "mode": "modification", "batiment": batiment})


@login_required
def batiment_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    batiment = get_object_or_404(Batiment, pk=pk)
    if request.method == "POST":
        batiment.delete()
        messages.success(request, "Bâtiment supprimé.")
        return redirect("thermo:batiment_liste")
    return render(request, "thermo/batiment_supprimer.html", {"batiment": batiment})


@login_required
def materiaux_hub(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "thermo/materiaux/hub.html",
        {
            "planchers": TypePlancher.objects.order_by("nom"),
            "murs": TypeMur.objects.order_by("nom"),
            "toitures": TypeToiture.objects.order_by("nom"),
            "ouvrants": TypeOuvrant.objects.order_by("nom"),
            "categories": CategorieBatiment.objects.order_by("nom"),
        },
    )


def _materiau_crud(
    request: HttpRequest,
    *,
    titre: str,
    form_cls,
    redirect_name: str,
    instance=None,
):
    if request.method == "POST":
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                messages.error(request, "Ce nom existe déjà. Choisissez un autre libellé.")
                return render(
                    request,
                    "thermo/materiaux/form.html",
                    {"form": form, "titre": titre, "mode": "modification" if instance else "creation"},
                )

            messages.success(request, "Enregistrement effectué.")
            return redirect(redirect_name)
    else:
        form = form_cls(instance=instance)

    return render(
        request,
        "thermo/materiaux/form.html",
        {"form": form, "titre": titre, "mode": "modification" if instance else "creation"},
    )


@login_required
def materiau_plancher_creer(request: HttpRequest) -> HttpResponse:
    return _materiau_crud(request, titre="Nouveau type de plancher", form_cls=TypePlancherForm, redirect_name="thermo:materiaux_hub")


@login_required
def materiau_plancher_modifier(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypePlancher, pk=pk)
    return _materiau_crud(
        request,
        titre="Modifier un type de plancher",
        form_cls=TypePlancherForm,
        redirect_name="thermo:materiaux_hub",
        instance=obj,
    )


@login_required
def materiau_plancher_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypePlancher, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Type supprimé.")
        except models.ProtectedError:
            messages.error(request, "Impossible de supprimer : ce type est utilisé par un bâtiment.")
        return redirect("thermo:materiaux_hub")
    return render(request, "thermo/materiaux/supprimer.html", {"titre": "Supprimer ce type de plancher ?", "objet": obj})


@login_required
def materiau_mur_creer(request: HttpRequest) -> HttpResponse:
    return _materiau_crud(request, titre="Nouveau type de mur", form_cls=TypeMurForm, redirect_name="thermo:materiaux_hub")


@login_required
def materiau_mur_modifier(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypeMur, pk=pk)
    return _materiau_crud(
        request,
        titre="Modifier un type de mur",
        form_cls=TypeMurForm,
        redirect_name="thermo:materiaux_hub",
        instance=obj,
    )


@login_required
def materiau_mur_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypeMur, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Type supprimé.")
        except models.ProtectedError:
            messages.error(request, "Impossible de supprimer : ce type est utilisé par un bâtiment.")
        return redirect("thermo:materiaux_hub")
    return render(request, "thermo/materiaux/supprimer.html", {"titre": "Supprimer ce type de mur ?", "objet": obj})


@login_required
def materiau_toiture_creer(request: HttpRequest) -> HttpResponse:
    return _materiau_crud(request, titre="Nouveau type de toiture", form_cls=TypeToitureForm, redirect_name="thermo:materiaux_hub")


@login_required
def materiau_toiture_modifier(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypeToiture, pk=pk)
    return _materiau_crud(
        request,
        titre="Modifier un type de toiture",
        form_cls=TypeToitureForm,
        redirect_name="thermo:materiaux_hub",
        instance=obj,
    )


@login_required
def materiau_toiture_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypeToiture, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Type supprimé.")
        except models.ProtectedError:
            messages.error(request, "Impossible de supprimer : ce type est utilisé par un bâtiment.")
        return redirect("thermo:materiaux_hub")
    return render(request, "thermo/materiaux/supprimer.html", {"titre": "Supprimer ce type de toiture ?", "objet": obj})


@login_required
def materiau_ouvrant_creer(request: HttpRequest) -> HttpResponse:
    return _materiau_crud(request, titre="Nouveau type d’ouvrant", form_cls=TypeOuvrantForm, redirect_name="thermo:materiaux_hub")


@login_required
def materiau_ouvrant_modifier(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypeOuvrant, pk=pk)
    return _materiau_crud(
        request,
        titre="Modifier un type d’ouvrant",
        form_cls=TypeOuvrantForm,
        redirect_name="thermo:materiaux_hub",
        instance=obj,
    )


@login_required
def materiau_ouvrant_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(TypeOuvrant, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Type supprimé.")
        except models.ProtectedError:
            messages.error(request, "Impossible de supprimer : ce type est utilisé par un bâtiment.")
        return redirect("thermo:materiaux_hub")
    return render(request, "thermo/materiaux/supprimer.html", {"titre": "Supprimer ce type d’ouvrant ?", "objet": obj})


@login_required
def categorie_batiment_creer(request: HttpRequest) -> HttpResponse:
    return _materiau_crud(request, titre="Nouveau type de bâtiment", form_cls=CategorieBatimentForm, redirect_name="thermo:materiaux_hub")


@login_required
def categorie_batiment_modifier(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(CategorieBatiment, pk=pk)
    return _materiau_crud(
        request,
        titre="Modifier un type de bâtiment",
        form_cls=CategorieBatimentForm,
        redirect_name="thermo:materiaux_hub",
        instance=obj,
    )


@login_required
def categorie_batiment_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    obj = get_object_or_404(CategorieBatiment, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Type supprimé.")
        except models.ProtectedError:
            messages.error(request, "Impossible de supprimer : ce type est utilisé par un bâtiment.")
        return redirect("thermo:materiaux_hub")
    return render(request, "thermo/materiaux/supprimer.html", {"titre": "Supprimer ce type de bâtiment ?", "objet": obj})
