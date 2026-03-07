from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("producto", "0002_producto_cantidad_tipo_producto"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producto",
            name="descripcion",
            field=models.TextField(blank=True, default="Sin descripcion", max_length=500),
        ),
    ]
