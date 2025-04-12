from rest_framework import serializers
from .models import Producto, Categoria, Subcategoria, Autor, Genero, Editorial
from rest_framework.validators import UniqueTogetherValidator

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

    def validate_nombre(self, value):
        categoria_id = self.instance.id if self.instance else None
        if Categoria.objects.filter(nombre__iexact=value).exclude(id=categoria_id).exists():
            raise serializers.ValidationError("Ya existe una categoría con ese nombre.")
        return value

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subcategoria.objects.all(),
                fields=['nombre', 'categoria'],  # Evitar duplicados por nombre y categoría
                message="Ya existe una subcategoría con ese nombre en esta categoría."
            )
        ]

    def validate_nombre(self, value):
        subcat_id = self.instance.id if self.instance else None
        if Subcategoria.objects.filter(nombre__iexact=value).exclude(id=subcat_id).exists():
            raise serializers.ValidationError("Ya existe una subcategoría con ese nombre.")
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
