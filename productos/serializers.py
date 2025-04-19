from rest_framework import serializers
from .models import Producto, Categoria, Autor, Genero, Editorial
from rest_framework.validators import UniqueTogetherValidator



class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

    def validate(self, data):
        instance = self.instance
        # Validamos en base al nombre de la categoría
        categoria_obj = data.get('categoria')
        if not categoria_obj:
            raise serializers.ValidationError({"categoria": "La categoría es requerida."})

        nombre_categoria = categoria_obj.nombre.lower()


        # Si es "accesorios", no deben enviarse esos campos
        if nombre_categoria == "Accesorios":
            if data.get('genero') or data.get('autor') or data.get('editorial'):
                raise serializers.ValidationError(
                    "Los campos 'genero', 'autor' y 'editorial' no deben enviarse para accesorios.")

        return data


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

    def validate_nombre(self, value):
        categoria_id = self.instance.id if self.instance else None
        if Categoria.objects.filter(nombre__iexact=value).exclude(id=categoria_id).exists():
            raise serializers.ValidationError("Ya existe una categoría con ese nombre.")
        return value


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = '__all__'

    def validate_nombre(self, value):
        # Si estamos actualizando, ignoramos el autor actual en la búsqueda
        autor_id = self.instance.id if self.instance else None
        if Autor.objects.filter(nombre__iexact=value).exclude(id=autor_id).exists():
            raise serializers.ValidationError("Este nombre de autor ya está registrado.")
        return value

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = '__all__'

    def validate_nombre(self, value):
        genero_id = self.instance.id if self.instance else None
        if Genero.objects.filter(nombre__iexact=value).exclude(id=genero_id).exists():
            raise serializers.ValidationError("Este género ya existe.")
        return value


class EditorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Editorial
        fields = '__all__'

    def validate_nombre(self, value):
        editorial_id = self.instance.id if self.instance else None
        if Editorial.objects.filter(nombre__iexact=value).exclude(id=editorial_id).exists():
            raise serializers.ValidationError("Esta editorial ya está registrada.")
        return value
