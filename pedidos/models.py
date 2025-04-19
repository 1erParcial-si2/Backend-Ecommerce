from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
import uuid
from productos.models import Producto


class Cupon(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cupones'
    )
    codigo = models.CharField(max_length=20, unique=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=2,
                                    help_text="Porcentaje de descuento, ej: 25.00 para 25%")
    estado = models.BooleanField(default=True)
    fecha_exp = models.DateField()

    def __str__(self):
        return f"{self.codigo} - {self.usuario.email}"

    def es_valido(self):
        return self.estado and self.fecha_exp >= date.today()


class Pedido(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    cupon = models.ForeignKey('Cupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')

    calificacion = models.IntegerField(
        null=True, blank=True,
        help_text="Calificación del pedido (opcional, del 1 al 5 por ejemplo)"
    )

    fecha_pedido  = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en que se realizó el pedido"
    )

    descuento = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0.00,
        help_text="Descuento aplicado en porcentaje, ej: 15.00 = 15%"
    )

    total = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total del pedido después del descuento"
    )

    activo = models.BooleanField(default=True)

    def calcular_total(self):
        total = sum([detalle.subtotal for detalle in self.detalles.all()])
        if self.descuento:
            total -= total * (self.descuento / Decimal(100))
        self.total = total
        self.save(update_fields=['total'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guardar primero para que existan los detalles
        self.calcular_total()

        # ✅ Si el pedido tiene un cupón, desactivarlo
        if self.cupon and self.cupon.es_valido():
            self.descuento = Decimal(25.00)  # puedes obtener del cupón si lo necesitas
            self.cupon.estado = False
            self.cupon.save()

        # ✅ Si el pedido supera los 500bs, asignar un nuevo cupón
        if self.total >= 500:
            Cupon.objects.create(
                usuario=self.usuario,
                codigo=str(uuid.uuid4())[:8],  # puedes generar un código único
                estado=True,
                fecha_exp=date.today().replace(year=date.today().year + 1)
            )


    def __str__(self):
     return f"Pedido #{self.id} - {self.usuario}"


class DetallePedido(models.Model):
        pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles', null=True)
        producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
        cantidad = models.PositiveIntegerField()
        precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
        subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

        def save(self, *args, **kwargs):
            self.precio_unitario = self.producto.precio
            self.subtotal = self.precio_unitario * self.cantidad
            super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.cantidad} x {self.producto.nombre}"

