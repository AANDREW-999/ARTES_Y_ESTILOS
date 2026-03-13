from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notificacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "categoria",
                    models.CharField(
                        choices=[("movimiento", "Movimiento"), ("stock", "Stock"), ("cuenta", "Cuenta")],
                        max_length=20,
                    ),
                ),
                (
                    "estilo",
                    models.CharField(
                        choices=[("success", "Success"), ("info", "Info"), ("warning", "Warning"), ("error", "Error")],
                        default="info",
                        max_length=20,
                    ),
                ),
                ("titulo", models.CharField(max_length=120)),
                ("mensaje", models.CharField(max_length=255)),
                (
                    "nivel_stock",
                    models.CharField(
                        blank=True,
                        choices=[("agotado", "Agotado"), ("bajo", "Bajo"), ("medio", "Medio"), ("alto", "Alto")],
                        max_length=20,
                    ),
                ),
                ("leida", models.BooleanField(default=False)),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-creada_en"]},
        ),
    ]
