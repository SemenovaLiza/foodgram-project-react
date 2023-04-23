from webcolors import name_to_hex
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipesIngredient


class ColorSerializer(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        data = name_to_hex(data)
        return data


class TagSerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_car', 'name', 'image', 'text', 'cooking_time'
        )
