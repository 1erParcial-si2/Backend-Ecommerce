from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UsuarioSerializer, RolSerializer, PermisoSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import Rol, Permiso
from .mixins import PermisoRequeridoMixin

from .permissions import TienePermisoPersonalizado

Usuario = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    swagger_tags = ['Usuarios']
    permiso_por_accion = {
        'list': 'ver_usuarios',
        'create': 'crear_usuarios',
        'update': 'editar_usuario',
        'partial_update': 'editar_usuario',
        'destroy': 'eliminar_usuario',
    }

    def get_permissions(self):
        # Solo en 'list' quieres permitir acceso público
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    swagger_tags = ['Roles']
    permiso_por_accion = {
        'list': 'ver_roles',
        'create': 'crear_roles',
        'update': 'editar_rol',
        'partial_update': 'editar_rol',
        'destroy': 'eliminar_rol',
    }

class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    swagger_tags = ['Permisos']
    permiso_por_accion = {
        'list': 'ver_permisos',
        'create': 'crear_permisos',
        'update': 'editar_permiso',
        'partial_update': 'editar_permiso',
        'destroy': 'eliminar_permiso',
    }
class LoginView(ObtainAuthToken):
    swagger_tags = ['Login']

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise AuthenticationFailed('Email y password son requeridos.')

        user = authenticate(request, username=username, password=password)

        if user is None:
            raise AuthenticationFailed('Credenciales inválidas')

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        return Response({'token': token.key, 'user_id': user.id})
