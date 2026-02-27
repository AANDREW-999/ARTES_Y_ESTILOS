
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('documento', models.CharField(max_length=20, unique=True, verbose_name='Documento')),
                ('tipo_documento', models.CharField(choices=[('CC', 'Cédula de ciudadanía'), ('TI', 'Tarjeta de identidad'), ('CE', 'Cédula de extranjería'), ('NIT', 'NIT'), ('PAS', 'Pasaporte')], max_length=10, verbose_name='Tipo de documento')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('apellido', models.CharField(max_length=100, verbose_name='Apellido')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='Teléfono')),
                ('correo_electronico', models.EmailField(blank=True, max_length=100, null=True, verbose_name='Correo electrónico')),
                ('direccion', models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección')),
                ('ciudad', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ciudad')),
                ('departamento', models.CharField(blank=True, max_length=45, null=True, verbose_name='Departamento')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['-created_at'],
            },
        ),
    ]
