from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (CustomUser, Favorite, Ingredient, Recipe,
                            RecipesIngredient, ShoppingCart, Subscription, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import RecipeFilter
from .pagination import Pagination
from .serializers import (AddRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    """Вывод списка тегов/вывод конкретоного тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    """Вывод списка ингредиентов/вывод конкретоного ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = (r'^name', )


class RecipeViewSet(ModelViewSet):
    """Отображение работы с рецептами."""
    queryset = Recipe.objects.all()
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    search_fields = (r'^name', )

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        return AddRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @action(detail=True, url_path='favorite', methods=['post', 'delete'])
    def add_to_favorite(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        if request.method == 'POST':
            favorite_data = {
                'recipe': recipe.id,
                'user': request.user.id
            }
            serializer = FavoriteSerializer(data=favorite_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        favorite = Favorite.objects.filter(recipe=recipe, user=request.user)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='shopping_cart', methods=['post', 'delete'])
    def add_to_shopping_cart(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        if request.method == 'POST':
            shopping_cart_data = {
                'recipe': recipe.id,
                'user': self.request.user.id
            }
            serializer = ShoppingCartSerializer(data=shopping_cart_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        shopping_cart = ShoppingCart.objects.filter(
            recipe=recipe, user=self.request.user
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='download_shopping_cart', methods=['get', ])
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        purchase_list = RecipesIngredient.objects.filter(recipe__in=recipes).values('ingredient').annotate(amount=Sum('amount'))
        text_file = f'Список покупок для {request.user.username} \n'
        for item in purchase_list:
            ingredient_id = item.get('ingredient')
            amount = item.get('amount')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            text_file += f'{ingredient.name} - {amount} {ingredient.measurement_unit} \n'

        response = HttpResponse(text_file, content_type='text.txt')
        response['Content-Disposition'] = 'attachment; filename="ttt.txt"'
        return response


class CustomUserViewSet(UserViewSet):
    """Отображение работы с пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = Pagination

    @action(detail=False, url_path='subscriptions', methods=['get'])
    def subscriptions(self, request):
        subsctiptions = self.request.user.following
        serializer = SubscriptionSerializer(subsctiptions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, url_path='subscribe', methods=['post', 'delete'])
    def subscribe(self, request, id):
        following = CustomUser.objects.get(pk=id)
        if request.method == 'POST':
            subscription = Subscription.objects.create(follower=self.request.user, following=following)
            serializer = SubscriptionSerializer(subscription, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(following=following, follower=self.request.user)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
