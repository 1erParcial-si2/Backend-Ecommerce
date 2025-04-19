from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CarritoSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Carrito, DetalleCarrito
from rest_framework.exceptions import ValidationError
from .models import Pedido,DetallePedido
from .serializers import  PedidoSerializer, DetallePedidoSerializer,DetalleCarritoSerializer

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

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Carrito.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'], url_path='activo')
    def obtener_carrito_activo(self, request):
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user, activo=True)
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='convertir-a-pedido')
    def convertir_a_pedido(self, request, pk=None):
        carrito = self.get_object()
        pedido = carrito.convertir_a_pedido()
        return Response({
            'mensaje': 'Carrito convertido a pedido exitosamente.',
            'pedido_id': pedido.id
        })

class DetalleCarritoViewSet(viewsets.ModelViewSet):
    queryset = DetalleCarrito.objects.all()
    serializer_class = DetalleCarritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DetalleCarrito.objects.filter(carrito__usuario=self.request.user, carrito__activo=True)

    def perform_create(self, serializer):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user, activo=True)
        serializer.save(carrito=carrito)
