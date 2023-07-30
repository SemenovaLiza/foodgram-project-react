from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipesIngredient,
                            ShoppingCart, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser, Subscription

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import Pagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (AddRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)


class CreateDeleteMixin(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """Добавление и удаление объекта из базы данных."""
    serializer_class = None
    model = None

    def post(self, request, id):
        user = request.user
        data = {
            'recipe': id,
            'user': user.id
        }
        serializer = self.serializer_class(
            data=data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

    def delete(self, request, id):
        user = request.user
        object = self.model.objects.filter(recipe=id, user=user)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class RecipeViewSet(CreateDeleteMixin, viewsets.ModelViewSet):
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


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def download_shopping_cart(request):
    """Скачать txt файл со списком ингредиентов
       для всех рецептов из списка покупок."""
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


class FavoriteViewSet(CreateDeleteMixin, RecipeViewSet):
    """Добавление/удаление рецепта из избранного."""
    serializer_class = FavoriteSerializer
    model = Favorite
    permission_classes = [IsAuthenticated, ]


class ShoppingCartViewSet(CreateDeleteMixin, RecipeViewSet):
    """Добавление/удаление рецепта из списка покупок."""
    serializer_class = ShoppingCartSerializer
    model = ShoppingCart
    permission_classes = [IsAuthenticated, ]


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


class SubscribeViewSet(CreateDeleteMixin, CustomUserViewSet):
    """Создание/удаление автора из подписок."""
    serializer_class = SubscriptionSerializer
    model = Subscription
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
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
