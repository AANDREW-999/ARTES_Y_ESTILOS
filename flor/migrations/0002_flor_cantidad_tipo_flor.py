from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flor", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flor",
            name="cantidad",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="flor",
            name="tipo_flor",
            field=models.CharField(
                choices=[
                    ("rosa", "Rosas"),
                    ("tulipan", "Tulipanes"),
                    ("girasol", "Girasoles"),
                    ("orquidea", "Orquideas"),
                    ("lirio", "Lirios"),
                    ("clavel", "Claveles"),
                    ("margarita", "Margaritas"),
                    ("hortensia", "Hortensias"),
                    ("mixtas", "Flores Mixtas"),
                    ("otras", "Otras"),
                ],
                default="otras",
                max_length=20,
            ),
        ),
    ]
