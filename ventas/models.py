from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


TIPO_VENTA_CHOICES = [
    ('BP', 'Bajo Pedido'),
    ('EI', 'Entrega Inmediata'),
]

FORMA_PAGO_CHOICES = [
    ('efectivo',      'Efectivo'),
    ('tarjeta',       'Tarjeta'),
    ('transferencia', 'Transferencia'),
    ('nequi',         'Nequi'),
    ('daviplata',     'Daviplata'),
]

IVA_CHOICES = [
    (0,  'Sin IVA (0%)'),
    (5,  '5%'),
    (19, '19%'),
]


class Venta(models.Model):
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='ventas'
    )

    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA_CHOICES)
    fecha      = models.DateField()

    mano_obra = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
        help_text='Costo de mano de obra'
    )
    forma_pago  = models.CharField(max_length=30, choices=FORMA_PAGO_CHOICES)
    descripcion = models.TextField(blank=True)
    con_domicilio = models.BooleanField(default=False)
    direccion     = models.CharField(max_length=200, blank=True, null=True)
    precio_envio  = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )
    nombre_domiciliario = models.CharField(max_length=100, blank=True, null=True,
                                           verbose_name='Nombre del domiciliario')
    telefono_domiciliario = models.CharField(max_length=20, blank=True, null=True,
                                              verbose_name='Teléfono del domiciliario')

    subtotal_sin_iva = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    iva_monto = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def recalcular_totales(self):
        from decimal import Decimal
        subtotal = sum(d.subtotal for d in self.detalles.all())
        subtotal += self.mano_obra or Decimal('0')
        if self.con_domicilio:
            subtotal += self.precio_envio or Decimal('0')
        self.subtotal_sin_iva = subtotal
        self.iva_monto        = Decimal('0')
        self.total            = subtotal 
        
    @property
    def total_arreglo(self):
        return sum(d.subtotal for d in self.detalles.all())

    def save(self, *args, **kwargs):
        if self.pk:
            self.recalcular_totales()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente}"

    class Meta:
        ordering  = ['-created_at']
        verbose_name       = 'Venta'
        verbose_name_plural = 'Ventas'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    arreglo = models.ForeignKey(
        'arreglo.Arreglo',
        on_delete=models.PROTECT
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio   = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text='Precio unitario en el momento de la venta'
    )
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.arreglo.nombre_flor} × {self.cantidad}"

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'
        
    
        
