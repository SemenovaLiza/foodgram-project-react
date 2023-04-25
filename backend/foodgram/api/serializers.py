from base64 import b64decode
from webcolors import name_to_hex
from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import Tag, Ingredient, Recipe, RecipesIngredient, User


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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ReInSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipesIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ing in ingredient:
            inger = Ingredient.objects.get(pk=ing.get('id'))

            RecipesIngredient.objects.create(recipe=recipe, ingredient=inger)
        return recipe