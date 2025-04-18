from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
import uuid
from productos.models import Producto



class Pedido(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')

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
        detalles = self.detalles.all()   #nuevo
        total_sin_descuento = sum([detalle.subtotal for detalle in self.detalles.all()])

        # Aplicar descuento según monto total
        if total_sin_descuento > 600:
            self.descuento = Decimal(25.00)
        elif total_sin_descuento > 400:
            self.descuento = Decimal(15.00)
        elif total_sin_descuento > 200:
            self.descuento = Decimal(10.00)
        else:
            self.descuento = Decimal(0.00)

        # Aplicar el descuento al total
       # total -= total * (self.descuento / Decimal(100))
        #self.total = total

        total_con_descuento = total_sin_descuento - (total_sin_descuento * (self.descuento / Decimal(100)))
        self.total = total_con_descuento


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guardar primero para que existan los detalles
        self.calcular_total()


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


# models.py
class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carritos')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Carrito de {self.usuario}"

    def calcular_total(self):
        return sum([detalle.subtotal for detalle in self.detalles.all()])

    def convertir_a_pedido(self):
        pedido = Pedido.objects.create(
            usuario=self.usuario,
            total=self.calcular_total(),
            descuento=0.00,  # Si quieres aplicar algún tipo de descuento en el pedido
            activo=True
        )

        for detalle in self.detalles.all():
            DetallePedido.objects.create(
                pedido=pedido,
                producto=detalle.producto,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal
            )

        self.activo = False  # Desactivar el carrito
        self.save()

        return pedido


class DetalleCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='detalles')
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
