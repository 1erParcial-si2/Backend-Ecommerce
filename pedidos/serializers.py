from rest_framework import serializers
from .models import Pedido, DetallePedido
from datetime import date, timedelta
import uuid



class DetallePedidoSerializer(serializers.ModelSerializer):

    class Meta:
        model = DetallePedido
        fields = ['id','pedido',  'producto', 'cantidad', 'precio_unitario', 'subtotal']



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