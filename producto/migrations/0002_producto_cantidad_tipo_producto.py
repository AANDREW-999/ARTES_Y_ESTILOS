from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producto", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="cantidad",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="producto",
            name="tipo_producto",
            field=models.CharField(
                choices=[
                    ("chocolates", "Chocolates"),
                    ("globos", "Globos"),
                    ("tarjetas", "Tarjetas"),
                    ("peluches", "Peluches"),
                    ("vinos", "Vinos"),
                    ("dulces", "Dulces"),
                    ("cajas_regalo", "Cajas de regalo"),
                    ("decoraciones", "Decoraciones"),
                    ("velas", "Velas aromaticas"),
                    ("otros", "Otros"),
                ],
                default="otros",
                max_length=30,
            ),
        ),
    ]
