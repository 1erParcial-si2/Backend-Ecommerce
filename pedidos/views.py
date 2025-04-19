from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import Cupon, Pedido
from .serializers import CuponSerializer, PedidoSerializer


# ViewSet para Cupones
class CuponViewSet(viewsets.ModelViewSet):
    queryset = Cupon.objects.all()
    serializer_class = CuponSerializer

    # Acción para obtener los cupones del usuario logueado
    @action(detail=False, methods=['get'], url_path='mis-cupones')
    def mis_cupones(self, request):
        cupones = Cupon.objects.filter(usuario=request.user, estado=True)
        serializer = self.get_serializer(cupones, many=True)
        return Response(serializer.data)


# ViewSet para Pedidos
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def perform_create(self, serializer):
        cupon_codigo = self.request.data.get('cupon_codigo', None)
        usuario = self.request.user
        cupon = None

        with transaction.atomic():
            # Crear el pedido asociado al usuario
            pedido = serializer.save(usuario=usuario)

            # Validar y aplicar el cupón si se envió
            if cupon_codigo:
                try:
                    cupon = Cupon.objects.get(codigo=cupon_codigo, usuario=usuario, estado=True)
                    if not cupon.es_valido():
                        raise ValidationError("Cupón no válido o expirado.")
                    pedido.cupon = cupon
                    pedido.descuento = cupon.descuento
                    pedido.save()

                    # Desactivar el cupón después de usarlo
                    cupon.estado = False
                    cupon.save()

                except Cupon.DoesNotExist:
                    raise ValidationError("Cupón inválido o ya usado")

            # Calcular el total del pedido
            pedido.calcular_total()
