from base64 import b64decode
from webcolors import name_to_hex
from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import Tag, Recipe, User, RecipesTag


class ColorSerializer(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        data = name_to_hex(data)
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class TagSerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class AddRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'tags', 'text', 'image', 'author', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipesTag.objects.create(recipe=recipe, tag=tag)
        return recipe


class ListRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'tags', 'text', 'image', 'author', 'cooking_time')
        read_only_fields = ('tags',)
