from django.db import models
from proveedores.models import Proveedor

# --- Definiciones de Choices para Compra ---

FORMA_PAGO_CHOICES = [
    ('EFECTIVO', 'Efectivo'),
    ('TRANSFERENCIA', 'Transferencia'),
    ('TARJETA', 'Tarjeta Debito/Credito'),
]

MEDIO_PAGO_CHOICES = [
    ('EFECTIVO', 'Efectivo'),
    ('TRANSFERENCIA', 'Transferencia'),
    ('TARJETA', 'Tarjeta Debito/Credito'),
]

# --- Modelo Compra ---

class Compra(models.Model):
    # id BIGINT se crea automáticamente como Primary Key si no se define, 
    # pero si quieres usar explícitamente BigAutoField:
    id = models.BigAutoField(primary_key=True)
    
    # Datos numéricos y financieros (agregados)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Subtotal")
    total_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Compra")
    
    # Información de la transacción
    descripcion = models.CharField(max_length=255, verbose_name="Descripción", blank=True)
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES, verbose_name="Forma de Pago", blank=True)
    medio_pago = models.CharField(max_length=20, choices=MEDIO_PAGO_CHOICES, verbose_name="Medio de Pago", blank=True)
    
    # Fechas
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento", blank=True, null=True)
    
    # Relación con Proveedor (ForeignKey real)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name="Proveedor")
    
    # Ubicación y Proceso
    departamento = models.CharField(max_length=45, verbose_name="Departamento", blank=True)
    ciudad = models.CharField(max_length=45, verbose_name="Ciudad", blank=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    def __str__(self):
        return f"Compra {self.id} - {self.descripcion}"

    def calcular_totales(self):
        """Calcula automáticamente los totales de la compra"""
        detalles = self.detallecompra_set.all()
        self.subtotal = sum(d.cantidad * d.precio for d in detalles)
        total_descuento = self.subtotal * (self.descuento / 100) if self.descuento > 0 else 0
        self.total_compra = self.subtotal - total_descuento
        self.save()


# --- Modelo DetalleCompra ---

class DetalleCompra(models.Model):
    """Modelo para guardar cada línea de producto en una compra"""
    id = models.BigAutoField(primary_key=True)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    
    # Información del producto
    rif = models.CharField(max_length=100, verbose_name="RIF", blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad")
    
    # Total de la línea
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Subtotal")
    
    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"
        ordering = ['id']

    def __str__(self):
        return f"Detalle {self.id} - Compra {self.compra.id} - {self.cantidad} x ${self.precio}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio
        super().save(*args, **kwargs)