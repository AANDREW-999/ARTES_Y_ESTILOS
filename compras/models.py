from django.db import models

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
    
    # Datos numéricos y financieros
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento")
    iva = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="IVA")
    total_compra = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total Compra")
    
    # Relaciones (Foreign Keys)
    # Asumiendo que tienes un modelo llamado Producto y uno de Proveedor
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT, verbose_name="Producto")
    # En la imagen aparece compra_id, si es una relación recursiva o a una cabecera:
    # cabecera_compra = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    # Información de la transacción
    descripcion = models.CharField(max_length=45, verbose_name="Descripción")
    forma_pago = models.CharField(max_length=20, choices=FORMA_PAGO_CHOICES, verbose_name="Forma de Pago")
    medio_pago = models.CharField(max_length=20, choices=MEDIO_PAGO_CHOICES, verbose_name="Medio de Pago")
    
    # Fechas (En la imagen son VARCHAR, pero en Django lo ideal es DateField)
    fecha_emision = models.DateField(verbose_name="Fecha de Emisión")
    fecha_vencimiento = models.DateField(verbose_name="Fecha de Vencimiento")
    
    # Ubicación y Proceso
    proveedor_id = models.CharField(max_length=45, verbose_name="ID Proveedor") # Podría ser ForeignKey a un modelo Proveedor
    departamento = models.CharField(max_length=45, verbose_name="Departamento")
    ciudad = models.CharField(max_length=45, verbose_name="Ciudad")
    proceso = models.CharField(max_length=45, verbose_name="Proceso")

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    def __str__(self):
        return f"Compra {self.id} - {self.descripcion}"