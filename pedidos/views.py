from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CarritoSerializer
from rest_framework.permissions import IsAuthenticated
from itertools import combinations

from .models import Carrito, DetalleCarrito
from rest_framework.exceptions import ValidationError
from .models import Pedido, DetallePedido
from .serializers import PedidoSerializer, DetallePedidoSerializer, DetalleCarritoSerializer
from drf_yasg.utils import swagger_auto_schema
from .schemas import (
    carrito_response, carrito_request, 
    detalle_carrito_response, detalle_carrito_request,
    pedido_conversion_response
)

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer

    def perform_create(self, serializer):
        detalle = serializer.save()  # Guardamos el detalle
        # Obtenemos el pedido asociado al detalle
        pedido = detalle.pedido
        pedido.calcular_total()  # Recalcular el total después de agregar el detalle
        pedido.save()  # Guardar el pedido con el nuevo total


# ViewSet para Pedidos
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def perform_create(self, serializer):
        pedido = serializer.save()
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

    @action(detail=False, methods=['get'], url_path='combinaciones-ml', permission_classes=[])
    def combinaciones_ml(self, request):
        """
        Genera datos para machine learning donde:
        - Target: Exactamente 1 producto
        - Input: Todos los demás productos del pedido
        
        Exporta datos en formato JSON o CSV con solo dos columnas: input_productos y target_producto
        """
        format_type = request.query_params.get('format', 'json')
        
        # Obtener pedidos con prefetch para optimizar
        pedidos = Pedido.objects.prefetch_related('detalles__producto').all()
        
        resultado = []
        
        for pedido in pedidos:
            productos = list(pedido.detalles.values_list('producto_id', flat=True))
            
            # Necesitamos al menos 2 productos (1 para input y 1 para target)
            if len(productos) < 2:
                continue
            
            # Para cada producto, ese producto es el target y el resto es el input
            for target_idx, target_product in enumerate(productos):
                # El input es todos los productos excepto el target
                input_products = [p for idx, p in enumerate(productos) if idx != target_idx]
                
                resultado.append({
                    "input": input_products,
                    "target": target_product  # Target es solo un producto
                })
        
        # Generación de CSV si se solicita
        if format_type.lower() == 'csv':
            import csv
            from django.http import HttpResponse
            
            # Configurar la respuesta HTTP para forzar la descarga
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="recomendaciones_ml.csv"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            
            writer = csv.writer(response)
            writer.writerow(['input_productos', 'target_producto'])
            
            for item in resultado:
                # Convertir lista de IDs de productos a string
                input_str = ','.join(map(str, item['input']))
                
                writer.writerow([
                    input_str,
                    item['target']
                ])
            
            return response
        
        # Para JSON, mantenemos la estructura de lista
        return Response(resultado)

    @action(detail=False, methods=['get'], url_path='descargar-ml-csv', permission_classes=[])
    def descargar_ml_csv(self, request):
        """
        Descarga directamente un archivo CSV con datos para machine learning:
        - Target: Exactamente 1 producto
        - Input: Todos los demás productos del pedido
        """
        # Obtener pedidos con prefetch para optimizar
        pedidos = Pedido.objects.prefetch_related('detalles__producto').all()
        
        resultado = []
        
        for pedido in pedidos:
            productos = list(pedido.detalles.values_list('producto_id', flat=True))
            
            # Necesitamos al menos 2 productos (1 para input y 1 para target)
            if len(productos) < 2:
                continue
            
            # Para cada producto, ese producto es el target y el resto es el input
            for target_idx, target_product in enumerate(productos):
                # El input es todos los productos excepto el target
                input_products = [p for idx, p in enumerate(productos) if idx != target_idx]
                
                resultado.append({
                    "input": input_products,
                    "target": target_product
                })
        
        # Generar CSV
        import csv
        from django.http import HttpResponse
        
        # Configurar la respuesta HTTP para forzar la descarga
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="recomendaciones_ml.csv"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        
        writer = csv.writer(response)
        writer.writerow(['input_productos', 'target_producto'])
        
        for item in resultado:
            # Convertir lista de IDs de productos a string
            input_str = ','.join(map(str, item['input']))
            
            writer.writerow([
                input_str,
                item['target']
            ])
        
        return response

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: carrito_response})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: carrito_response})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @swagger_auto_schema(request_body=carrito_request, responses={201: carrito_response})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        # Manejar el caso de Swagger cuando no hay usuario autenticado
        if not self.request.user.is_authenticated:
            return Carrito.objects.none()
        return Carrito.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @swagger_auto_schema(responses={200: carrito_response})
    @action(detail=False, methods=['get'], url_path='activo')
    def obtener_carrito_activo(self, request):
        # Manejar el caso de Swagger cuando no hay usuario autenticado
        if not request.user.is_authenticated:
            return Response({"error": "Usuario no autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
            
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user, activo=True)
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: pedido_conversion_response})
    @action(detail=True, methods=['post'], url_path='convertir-a-pedido')
    def convertir_a_pedido(self, request, pk=None):
        # Manejar el caso de Swagger cuando no hay usuario autenticado
        if not request.user.is_authenticated:
            return Response({"error": "Usuario no autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
            
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

    @swagger_auto_schema(responses={200: detalle_carrito_response})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: detalle_carrito_response})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @swagger_auto_schema(request_body=detalle_carrito_request, responses={201: detalle_carrito_response})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        # Manejar el caso de Swagger cuando no hay usuario autenticado
        if not self.request.user.is_authenticated:
            return DetalleCarrito.objects.none()
        return DetalleCarrito.objects.filter(carrito__usuario=self.request.user, carrito__activo=True)

    def perform_create(self, serializer):
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user, activo=True)
        serializer.save(carrito=carrito) 