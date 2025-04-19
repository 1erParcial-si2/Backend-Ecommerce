from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import Pedido,DetallePedido
from .serializers import  PedidoSerializer, DetallePedidoSerializer

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer

    def perform_create(self, serializer):
        detalle = serializer.save()  # Guardamos el detalle
        # Obtenemos el pedido asociado al detalle
        pedido = detalle.pedido
        pedido.calcular_total()  # Recalcular el total después de agregar el detalle
        pedido.save()  # Guardar el pedido con el nuevo total

        return Response(serializer.data, status=status.HTTP_201_CREATED)



# ViewSet para Pedidos
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def perform_create(self, serializer):
        pedido = serializer.save(usuario=self.request.user)
        pedido.calcular_total()
        pedido.save()

    @action(detail=True, methods=['post'], url_path='calcular-total')
    def calcular_total(self, request, pk=None):
        pedido = self.get_object()
        pedido.calcular_total()
        pedido.save()
        return Response({'total_actualizado': str(pedido.total)})

    @action(detail=True, methods=['post'], url_path='calificar')
    def calificar(self, request, pk=None):
        pedido = self.get_object()

        # Obtenemos la calificación del cuerpo de la solicitud
        calificacion = request.data.get('calificacion')

        if calificacion is None:
            return Response({'detail': 'Debe proporcionar una calificación.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validamos que la calificación esté en el rango correcto (1-5)
        if not (1 <= calificacion <= 5):
            return Response({'detail': 'La calificación debe estar entre 1 y 5.'}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizamos la calificación
        pedido.calificacion = calificacion
        pedido.save()

        return Response({'detail': 'Calificación actualizada con éxito.'}, status=status.HTTP_200_OK)