from rest_framework import serializers
from .models import Pedido, DetallePedido,Producto
from .models import Carrito, DetalleCarrito
from productos.serializers import ProductoSerializer
from datetime import date, timedelta
import uuid




class DetallePedidoSerializer(serializers.ModelSerializer):

    class Meta:
        model = DetallePedido
        fields = ['id','pedido',  'producto', 'cantidad', 'precio_unitario', 'subtotal']

        def create(self, validated_data):
            producto = validated_data['producto']
            cantidad = validated_data['cantidad']

            # Verificar stock disponible
            if producto.stock < cantidad:
                raise serializers.ValidationError(
                    f"No hay suficiente stock para el producto '{producto.nombre}'. Stock actual: {producto.stock}"
                )

            # Descontar stock
            producto.stock -= cantidad
            producto.save()

            # Calcular precio y subtotal
            validated_data['precio_unitario'] = producto.precio
            validated_data['subtotal'] = producto.precio * cantidad

            return super().create(validated_data)



class PedidoSerializer(serializers.ModelSerializer):


    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'descuento', 'total', 'fecha_pedido']
        read_only_fields = ['id', 'fecha_pedido']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles',[])
        pedido = Pedido.objects.create(**validated_data)

        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)

        pedido.calcular_total()  # Calcula el total y aplica el descuento

        return pedido


class DetalleCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = DetalleCarrito
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['precio_unitario', 'subtotal']


class CarritoSerializer(serializers.ModelSerializer):
    detalles = DetalleCarritoSerializer(many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'activo', 'detalles']
        read_only_fields = ['usuario']