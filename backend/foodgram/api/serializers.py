from base64 import b64decode
from webcolors import name_to_hex
from rest_framework import serializers
from django.core.files.base import ContentFile

from recipes.models import Tag, Recipe, User, RecipesTag, Favorite, ShoppingCart, Subscribtion


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
    is_sub = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_sub')
    
    def get_is_sub(self, obj):
        following = User.objects.get(pk=obj.id)
        sub = Subscribtion.objects.filter(following=following, follower=self.context['request'].user).exists()
        return sub


class TagSerializer(serializers.ModelSerializer):
    color = ColorSerializer()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class AddRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'tags', 'text', 'image', 'author', 'is_favorite', 'is_in_shopping_cart', 'cooking_time')

    def get_is_favorite(self, obj):
        recipe = Recipe.objects.get(pk=obj.id)
        favorite = Favorite.objects.filter(recipe=recipe, user=self.context['request'].user).exists()
        return favorite

    def get_is_in_shopping_cart(self, obj):
        recipe = Recipe.objects.get(pk=obj.id)
        shopping_cart = ShoppingCart.objects.filter(recipe=recipe, user=self.context['request'].user).exists()
        return shopping_cart


class ListRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'tags', 'text', 'image', 'author', 'cooking_time', 'is_favorite', 'is_in_shopping_cart')
        read_only_fields = ('tags',)

    def get_is_favorite(self, obj):
        recipe = Recipe.objects.get(pk=obj.id)
        favorite = Favorite.objects.filter(recipe=recipe, user=self.context['request'].user).exists()
        return favorite

    def get_is_in_shopping_cart(self, obj):
        recipe = Recipe.objects.get(pk=obj.id)
        shopping_cart = ShoppingCart.objects.filter(recipe=recipe, user=self.context['request'].user).exists()
        return shopping_cart

class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ShowSubscriptionsSerializer(serializers.ModelSerializer):
    is_sub = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_sub')
    
    def get_is_sub(self, obj):
        following = User.objects.get(pk=obj.id)
        sub = Subscribtion.objects.filter(following=following, follower=request.user).exists()
        return sub


class SubSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    email = serializers.ReadOnlyField(source='following.email')
    is_sub = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscribtion
        fields = ('id', 'username', 'email', 'is_sub', 'recipes')

    def get_is_sub(self, obj):
        sub = Subscribtion.objects.filter(following=obj.following, follower=self.context['request'].user).exists()
        return sub

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.following)
        return ShortRecipeSerializer(recipes, many=True).data
