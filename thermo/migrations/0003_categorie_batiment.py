from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


def seed_categories(apps, schema_editor):
    CategorieBatiment = apps.get_model("thermo", "CategorieBatiment")
    defaults = [
        "École",
        "Hôpital",
        "Immeuble",
        "Bureau",
        "Commerce",
        "Industriel",
    ]
    for nom in defaults:
        CategorieBatiment.objects.get_or_create(nom=nom, defaults={"actif": True})


def backfill_batiment_categories(apps, schema_editor):
    Batiment = apps.get_model("thermo", "Batiment")
    CategorieBatiment = apps.get_model("thermo", "CategorieBatiment")

    immeuble = CategorieBatiment.objects.filter(nom="Immeuble").first()
    if not immeuble:
        immeuble = CategorieBatiment.objects.create(nom="Immeuble", actif=True)

    Batiment.objects.filter(categorie__isnull=True).update(categorie_id=immeuble.pk)


class Migration(migrations.Migration):
    dependencies = [
        ("thermo", "0002_seed_comptes_et_types"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategorieBatiment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=120, unique=True)),
                ("actif", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["nom"],
            },
        ),
        migrations.AddField(
            model_name="batiment",
            name="categorie",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="thermo.categoriebatiment",
                verbose_name="Type de bâtiment",
            ),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
        migrations.RunPython(backfill_batiment_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="batiment",
            name="categorie",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="thermo.categoriebatiment",
                verbose_name="Type de bâtiment",
            ),
        ),
    ]
