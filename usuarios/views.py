from django.shortcuts import render

# Create your views here. es como el controller

from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UsuarioSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

Usuario = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # Validación del usuario
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise AuthenticationFailed('Email y password son requeridos.')

            # Verificar las credenciales del usuario
        user = authenticate(request, username=username, password=password)

        if user is None:
            raise AuthenticationFailed('Credenciales inválidas')

        # Eliminar el token anterior si existe (opcional, para asegurarse de que sea un nuevo token cada vez)
        Token.objects.filter(user=user).delete()

        # Crear un nuevo token
        token = Token.objects.create(user=user)

        return Response({'token': token.key, 'user_id': user.id})