from django.db import models
#from arreglos.models import Arreglo
from clientes.models import Cliente


TIPO_VENTA_CHOICES = [
    ('BP', 'Bajo Pedido'),
    ('EI', 'Entrega Inmediata'),
]

FORMA_PAGO_CHOICES = [
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
    ('transferencia', 'Transferencia'),
    ('nequi', 'Nequi'),
    ('daviplata', 'Daviplata'),
]


class Venta(models.Model):
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='ventas'
    )

    #arreglo = models.ForeignKey(
        #'arreglos.Arreglo',
        #on_delete=models.CASCADE,
       #related_name='ventas'
    #)

    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA_CHOICES)
    fecha = models.DateField(auto_now_add=True)

    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio unitario del arreglo'
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    forma_pago = models.CharField(
        max_length=30,
        choices=FORMA_PAGO_CHOICES
    )

    descripcion = models.TextField(blank=True)


    con_domicilio = models.BooleanField(default=False)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    precio_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def save(self, *args, **kwargs):
        subtotal = self.cantidad * self.precio

        if self.con_domicilio:
            self.total = subtotal + (self.precio_envio or 0)
        else:
            self.total = subtotal

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"
