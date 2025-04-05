from rest_framework import serializers
from django.contrib.auth import get_user_model

# Obtén el modelo de usuario (con tu configuración personalizada)
Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True)  # Esto oculta la contraseña en las respuestas, pero permite enviarla

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre_completo', 'telefono', 'direccion',
                  'password']  # Excluimos 'username' y mantenemos el 'email'
        extra_kwargs = {'password': {'write_only': True}}  # La contraseña solo se utilizará en la creación del usuario

    def create(self, validated_data):
        """Crea un usuario con contraseña encriptada"""
        # Extraemos la contraseña del diccionario de datos validados
        password = validated_data.pop('password')

        # Creamos el usuario con los datos validados (sin la contraseña aún)
        usuario = Usuario(**validated_data)

        # Encriptamos la contraseña
        usuario.set_password(password)

        # Guardamos el usuario en la base de datos
        usuario.save()

        return usuario
