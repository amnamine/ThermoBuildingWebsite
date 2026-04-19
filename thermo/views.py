from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BatimentForm
from .models import Batiment


@login_required
def tableau_de_bord(request: HttpRequest) -> HttpResponse:
    batiments = Batiment.objects.all()[:6]
    total = Batiment.objects.count()
    return render(
        request,
        "thermo/tableau_de_bord.html",
        {"batiments": batiments, "total": total},
    )


@login_required
def batiment_liste(request: HttpRequest) -> HttpResponse:
    batiments = Batiment.objects.all()
    return render(request, "thermo/batiment_liste.html", {"batiments": batiments})


@login_required
def batiment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    batiment = get_object_or_404(Batiment, pk=pk)
    return render(request, "thermo/batiment_detail.html", {"batiment": batiment})


@login_required
def batiment_creer(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BatimentForm(request.POST)
        if form.is_valid():
            batiment = form.save()
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
            return redirect("thermo:batiment_detail", pk=batiment.pk)
    else:
        form = BatimentForm(instance=batiment)
    return render(request, "thermo/batiment_form.html", {"form": form, "mode": "modification", "batiment": batiment})


@login_required
def batiment_supprimer(request: HttpRequest, pk: int) -> HttpResponse:
    batiment = get_object_or_404(Batiment, pk=pk)
    if request.method == "POST":
        batiment.delete()
        return redirect("thermo:batiment_liste")
    return render(request, "thermo/batiment_supprimer.html", {"batiment": batiment})
