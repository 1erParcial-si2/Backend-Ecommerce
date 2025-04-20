from rest_framework import serializers
from .models import Pedido, DetallePedido,Producto
from .models import Carrito, DetalleCarrito
from productos.serializers import ProductoSerializer
from datetime import date, timedelta
import uuid
from django.db import transaction




class DetallePedidoSerializer(serializers.ModelSerializer):
    # Incluir el objeto completo del producto
    producto = ProductoSerializer(read_only=True)
    
    # Campo para escritura (solo ID)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), source='producto', write_only=True
    )

    class Meta:
        model = DetallePedido
        fields = ['id', 'pedido', 'producto', 'producto_id', 'cantidad', 'precio_unitario', 'subtotal']


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
    # Incluir detalles en la respuesta (tanto para lectura como escritura)
    detalles = DetallePedidoSerializer(many=True, required=False)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'detalles', 'descuento', 'total', 'fecha_pedido', 'calificacion', 'activo']
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
        
    def validate_cantidad(self, value):
        """
        Verificar que la cantidad sea mayor que cero.
        """
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value
        
    def validate(self, data):
        """
        Verificar que haya suficiente stock para el producto.
        """
        cantidad = data.get('cantidad')
        producto = data.get('producto')
        
        # Verificar stock disponible
        if producto.stock < cantidad:
            raise serializers.ValidationError(
                f"No hay suficiente stock para el producto '{producto.nombre}'. Stock actual: {producto.stock}"
            )
            
        return data
    
    def create(self, validated_data):
        carrito = validated_data.get('carrito')
        producto = validated_data.get('producto')
        cantidad = validated_data.get('cantidad')
        
        # Buscar si el producto ya existe en el carrito
        with transaction.atomic():
            detalle_existente = DetalleCarrito.objects.filter(
                carrito=carrito,
                producto=producto
            ).first()
            
            if detalle_existente:
                # Verificar que haya suficiente stock para la cantidad aumentada
                cantidad_total = detalle_existente.cantidad + cantidad
                if producto.stock < cantidad_total:
                    raise serializers.ValidationError(
                        f"No hay suficiente stock para el producto '{producto.nombre}'. "
                        f"Stock actual: {producto.stock}, cantidad en carrito: {detalle_existente.cantidad}"
                    )
                
                # Actualizar cantidad del item existente
                detalle_existente.cantidad = cantidad_total
                detalle_existente.save()
                return detalle_existente
            else:
                # Crear nuevo detalle de carrito
                return super().create(validated_data)


class CarritoSerializer(serializers.ModelSerializer):
    detalles = DetalleCarritoSerializer(many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'activo', 'detalles']
        read_only_fields = ['usuario']