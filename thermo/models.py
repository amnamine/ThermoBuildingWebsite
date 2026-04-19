from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class CoefficientBase(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    k = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Coefficient de transmission surfacique (k).",
    )
    actif = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["nom"]

    def __str__(self) -> str:
        return f"{self.nom} (k={self.k})"


class TypePlancher(CoefficientBase):
    pass


class TypeMur(CoefficientBase):
    pass


class TypeToiture(CoefficientBase):
    pass


class TypeOuvrant(CoefficientBase):
    pass


class CategorieBatiment(models.Model):
    """
    Type de bâtiment (école, hôpital, etc.) tel que mentionné dans l'énoncé.
    """

    nom = models.CharField(max_length=120, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class Batiment(models.Model):
    nom = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    cree_le = models.DateTimeField(default=timezone.now, editable=False)

    categorie = models.ForeignKey(
        CategorieBatiment,
        verbose_name="Type de bâtiment",
        on_delete=models.PROTECT,
    )

    surface_habitable_m2 = models.DecimalField(
        "Surface habitable (m²)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    type_plancher = models.ForeignKey(TypePlancher, on_delete=models.PROTECT)
    surface_plancher_m2 = models.DecimalField(
        "Surface plancher (m²)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    type_mur = models.ForeignKey(TypeMur, on_delete=models.PROTECT)
    surface_mur_m2 = models.DecimalField(
        "Surface murs (m²)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    type_toiture = models.ForeignKey(TypeToiture, on_delete=models.PROTECT)
    surface_toiture_m2 = models.DecimalField(
        "Surface toiture (m²)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    type_ouvrant = models.ForeignKey(TypeOuvrant, on_delete=models.PROTECT)
    surface_ouvrants_m2 = models.DecimalField(
        "Surface ouvrants (m²)",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        ordering = ["-cree_le", "nom"]

    @property
    def deperdition_plancher(self) -> Decimal:
        return (self.type_plancher.k or Decimal("0")) * (self.surface_plancher_m2 or Decimal("0"))

    @property
    def deperdition_murs(self) -> Decimal:
        return (self.type_mur.k or Decimal("0")) * (self.surface_mur_m2 or Decimal("0"))

    @property
    def deperdition_toiture(self) -> Decimal:
        return (self.type_toiture.k or Decimal("0")) * (self.surface_toiture_m2 or Decimal("0"))

    @property
    def deperdition_ouvrants(self) -> Decimal:
        return (self.type_ouvrant.k or Decimal("0")) * (self.surface_ouvrants_m2 or Decimal("0"))

    @property
    def deperdition_totale(self) -> Decimal:
        return self.deperdition_murs + self.deperdition_plancher + self.deperdition_ouvrants + self.deperdition_toiture

    @property
    def consommation_kwh_m2_an(self) -> Decimal:
        # Interprétation pratique: on normalise la déperdition totale par la surface habitable,
        # afin d'obtenir un indicateur en kWh/m²/an, comme demandé dans l'énoncé.
        return self.deperdition_totale / self.surface_habitable_m2

    @staticmethod
    def classe_depuis_conso(c: Decimal) -> str:
        if c < Decimal("70"):
            return "A"
        if c <= Decimal("110"):
            return "B"
        if c <= Decimal("180"):
            return "C"
        if c <= Decimal("250"):
            return "D"
        if c <= Decimal("330"):
            return "E"
        if c <= Decimal("420"):
            return "F"
        return "G"

    @property
    def classe_energie(self) -> str:
        return self.classe_depuis_conso(self.consommation_kwh_m2_an)

    def __str__(self) -> str:
        return self.nom
