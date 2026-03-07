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
    nombre_domiciliario = models.CharField(max_length=120, blank=True, null=True)
    telefono_domiciliario = models.CharField(max_length=20, blank=True, null=True)
    precio_envio  = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(0)]
    )

    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, editable=False
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def recalcular_totales(self):
        """Recalcula subtotal y total desde los detalles (sin IVA)."""
        from decimal import Decimal
        subtotal = sum(d.subtotal for d in self.detalles.all())
        subtotal += self.mano_obra or Decimal('0')
        if self.con_domicilio:
            subtotal += self.precio_envio or Decimal('0')

        self.subtotal = subtotal
        self.total = subtotal

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
    TIPO_ITEM_CHOICES = [
        ('FLOR', 'Flor'),
        ('PRODUCTO', 'Producto'),
    ]

    tipo_item = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES)
    flor = models.ForeignKey('flor.Flor', on_delete=models.PROTECT, null=True, blank=True)
    producto = models.ForeignKey('producto.Producto', on_delete=models.PROTECT, null=True, blank=True)
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
        # Coherencia mínima entre tipo_item y FK
        if self.tipo_item == 'FLOR':
            self.producto = None
        elif self.tipo_item == 'PRODUCTO':
            self.flor = None

        self.subtotal = self.cantidad * self.precio
        super().save(*args, **kwargs)

    @property
    def item(self):
        return self.flor or self.producto

    @property
    def item_nombre(self):
        return getattr(self.item, 'nombre', '') if self.item else ''

    def __str__(self):
        return f"{self.item_nombre} × {self.cantidad}"

    class Meta:
        ordering = ['-created_at']
        verbose_name        = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'