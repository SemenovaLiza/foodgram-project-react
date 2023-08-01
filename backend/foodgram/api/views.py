from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipesIngredient,
                            ShoppingCart, Tag)
from rest_framework import views, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser, Subscription

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import PostDeleteMixin
from .pagination import Pagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (AddRecipeSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, SubscriptionSerializer,
                          TagSerializer)


@api_view(http_method_names=['GET', ])
@permission_classes([IsAuthenticated, ])
def download_shopping_cart(request):
    """Функция для скачивания списка ингредиентов
       из всех добавленых в список покупок рецептов."""
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


class RecipeViewSet(viewsets.ModelViewSet):
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


class CustomUserViewSet(UserViewSet):
    """Отображение работы с пользователями."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = Pagination

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(followers__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubscribeView(PostDeleteMixin, views.APIView):
    """Создание/удаление автора из подписок."""
    model_class = Subscription
    serializer_class = SubscribeSerializer
    obj_model = CustomUser
    object_name = 'following'


class FavoriteView(PostDeleteMixin, views.APIView):
    """ Добавление/удаление рецепта из избранного. """
    model_class = Favorite
    serializer_class = FavoriteSerializer
    obj_model = Recipe
    object_name = 'recipe'


class ShoppingCartView(FavoriteView):
    """Добавление/удаление рецепта из списка покупок."""
    model_class = ShoppingCart
    serializer_class = ShoppingCartSerializer
