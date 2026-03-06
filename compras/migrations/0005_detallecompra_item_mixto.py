from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("flor", "0002_flor_cantidad_tipo_flor"),
        ("producto", "0002_producto_cantidad_tipo_producto"),
        ("compras", "0004_compra_departamento"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="detallecompra",
            name="rif",
        ),
        migrations.AddField(
            model_name="detallecompra",
            name="flor",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="flor.flor"),
        ),
        migrations.AddField(
            model_name="detallecompra",
            name="producto",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="producto.producto"),
        ),
        migrations.AddField(
            model_name="detallecompra",
            name="tipo_item",
            field=models.CharField(choices=[("FLOR", "Flor"), ("PRODUCTO", "Producto")], default="PRODUCTO", max_length=20),
        ),
    ]
