from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipesIngredient,
                            RecipesTag, RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import CustomUser, Subscription


class CustomUserSerializer(UserSerializer):
    """Сериализатор для отображения списка пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        following = CustomUser.objects.get(pk=obj.id)
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.following.filter(following=following).exists()


class CreateCustomUserSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки на автора."""
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    email = serializers.ReadOnlyField(source='following.email')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id', 'username',
            'email', 'is_subscribed',
            'recipes', 'recipes_count'
        )
        read_only_fields = ('is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=request.user, following=obj
        ).exists()

    def get_recipes(self, obj):
        return ShortRecipeSerializer(obj.following.recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.following.recipes.count()


class RecipesIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка рецептов."""
    image = Base64ImageField()
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipesIngredientSerializer(
        many=True,
        source='ingredientsinrecipe')

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'tags',
            'text', 'image', 'author',
            'cooking_time', 'is_favorited',
            'is_in_shopping_cart', 'ingredients'
        )
        read_only_fields = (
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        ingredients = RecipesIngredient.objects.get(recipe=obj)
        return RecipesIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj.id).exists()


class AddRecipeSerializer(RecipeSerializer):
    """Сериализатор для создания рецепта."""
    ingredients = RecipesIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        read_only=False
    )
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipesIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        RecipesIngredient.objects.filter(recipe=instance).delete()
        RecipesTag.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image'):
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        self.create_tags(tags, instance)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""
    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return ShortRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор для корзины с рецептами."""
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
