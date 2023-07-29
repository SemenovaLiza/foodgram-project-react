from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipesIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import CustomUser, Subscription

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import Pagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (AddRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает список тегов/конкретный тег."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает список ингредиентов/конкретный ингредиент."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """Вывод работы с рецептами."""
    queryset = Recipe.objects.all()
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    search_fields = ('^name', )
    permission_classes = (IsAuthorOrAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        return AddRecipeSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk):
        return self.add_delete_obj(request, pk, FavoriteSerializer, Favorite)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        return self.add_delete_obj(
            request, pk, ShoppingCartSerializer, ShoppingCart
        )

    @action(detail=False, methods=['get', ],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        purchase_list = RecipesIngredient.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(ingredients_amount=Sum('amount'))

        text_file = f'Список покупок для {request.user.username} \n'
        for item in purchase_list:
            ingredient_id = item.get('ingredient')
            amount = item.get('ingredients_amount')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            text_file += (f'{ingredient.name} - {amount}'
                          f'{ingredient.measurement_unit} \n')

        response = HttpResponse(text_file, content_type='text.txt')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="purchase_list.txt"')
        return response

    def add_delete_obj(self, request, pk, obj_serializer, obj_model):
        recipe = Recipe.objects.get(pk=pk)
        if request.method == 'POST':
            data = {
                'recipe': recipe.id,
                'user': request.user.id
            }
            serializer = obj_serializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        object = obj_model.objects.filter(recipe=recipe, user=request.user)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomUserViewSet(UserViewSet):
    """Отображение работы с пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = Pagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(followers__follower=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, id):
        following = get_object_or_404(CustomUser, pk=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                following, data=request.data, context={'request': request}
            )
            if serializer.is_valid(raise_exception=True):
                Subscription.objects.create(follower=user, following=following)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        subscription = Subscription.objects.filter(
            following=following, follower=user
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
