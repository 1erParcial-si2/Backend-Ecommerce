from rest_framework import serializers
from .models import Pedido, DetallePedido, Cupon
from datetime import date, timedelta
import uuid


class CuponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupon
        fields = ['id', 'codigo', 'estado', 'fecha_exp']


class DetallePedidoSerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(queryset=Pedido.objects.all(), write_only=True)  # Referencia solo por el ID

    class Meta:
        model = DetallePedido
        fields = ['pedido','producto', 'cantidad', 'precio_unitario', 'subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)
    cupon_codigo = serializers.CharField(write_only=True, required=False)
    nuevo_cupon = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'usuario', 'cupon_codigo', 'descuento', 'total', 'fecha_pedido', 'detalles', 'nuevo_cupon']

    def validate_descuento(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("El descuento debe estar entre 0% y 100%.")
        return value

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        cupon_codigo = validated_data.pop('cupon_codigo', None)
        usuario = validated_data['usuario']

        cupon = None
        if cupon_codigo:
            try:
                cupon = Cupon.objects.get(codigo=cupon_codigo, usuario=usuario, estado=True)
                if not cupon.es_valido():
                    raise serializers.ValidationError("Cupón no válido o expirado.")
                validated_data['cupon'] = cupon
                validated_data['descuento'] = cupon.descuento
            except Cupon.DoesNotExist:
                raise serializers.ValidationError("Cupón inválido o ya usado")

        pedido = Pedido.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)

        pedido.calcular_total()

        # Desactivar cupón si se usó
        if cupon:
            cupon.estado = False
            cupon.save()

        # Crear nuevo cupón si el pedido supera los 500 Bs
        self.nuevo_cupon = None
        if pedido.total > 500:
            nuevo_cupon = Cupon.objects.create(
                usuario=usuario,
                codigo=str(uuid.uuid4())[:8],
                descuento=25.00,
                estado=True,
                fecha_exp=date.today() + timedelta(days=30)
            )
            self.nuevo_cupon = nuevo_cupon

        return pedido

    def get_nuevo_cupon(self, obj):
        if hasattr(self, 'nuevo_cupon') and self.nuevo_cupon:
            return CuponSerializer(self.nuevo_cupon).data
        return None
