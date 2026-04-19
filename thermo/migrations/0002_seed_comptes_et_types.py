from __future__ import annotations

from decimal import Decimal

from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed_comptes_et_types(apps, schema_editor):
    User = apps.get_model("auth", "User")

    def upsert_user(username: str, password: str, is_staff: bool, is_superuser: bool):
        user, _created = User.objects.get_or_create(
            username=username,
            defaults={
                "is_staff": is_staff,
                "is_superuser": is_superuser,
            },
        )
        # Force le mot de passe à la valeur demandée.
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.password = make_password(password)
        user.save()

    upsert_user("admin", "admin", is_staff=True, is_superuser=True)
    upsert_user("user", "user", is_staff=False, is_superuser=False)

    TypePlancher = apps.get_model("thermo", "TypePlancher")
    TypeMur = apps.get_model("thermo", "TypeMur")
    TypeToiture = apps.get_model("thermo", "TypeToiture")
    TypeOuvrant = apps.get_model("thermo", "TypeOuvrant")

    def upsert_type(Model, nom: str, k: str):
        Model.objects.get_or_create(nom=nom, defaults={"k": Decimal(k), "actif": True})

    # Valeurs réalistes (mais simplifiées) pour alimenter les listes déroulantes.
    upsert_type(TypePlancher, "Plancher parquet", "0.6000")
    upsert_type(TypePlancher, "Plancher bois", "0.4500")
    upsert_type(TypePlancher, "Plancher béton", "0.8000")

    upsert_type(TypeMur, "Mur sans isolation", "1.4000")
    upsert_type(TypeMur, "Mur double paroi", "1.0000")
    upsert_type(TypeMur, "Mur double paroi avec isolation", "0.6000")

    upsert_type(TypeToiture, "Toiture plate", "0.9000")
    upsert_type(TypeToiture, "Toiture inclinée", "0.8000")
    upsert_type(TypeToiture, "Toiture isolée", "0.4500")

    upsert_type(TypeOuvrant, "Fenêtre simple vitrage", "2.8000")
    upsert_type(TypeOuvrant, "Fenêtre double vitrage", "1.6000")
    upsert_type(TypeOuvrant, "Porte", "2.0000")


class Migration(migrations.Migration):
    dependencies = [
        ("thermo", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(seed_comptes_et_types, migrations.RunPython.noop),
    ]

