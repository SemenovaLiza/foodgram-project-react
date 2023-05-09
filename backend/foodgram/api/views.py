from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django.db.models import Sum
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404

from .serializers import TagSerializer, AddRecipeSerializer, ListRecipeSerializer, FavoriteSerializer, ShoppingCartSerializer, ListCustomUserSerializer, SubSerializer, IngredientSerializer, IngredientRecipeSerializer, rIngredientRecipeSerializer
from recipes.models import Tag, Recipe, Favorite, ShoppingCart, CustomUser, Subscribtion, Ingredient, RecipesIngredient


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    pass


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ListRecipeSerializer
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
                return Response(serializer.data, status=status.HTTP_201_CREATED)

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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            shopping_cart = ShoppingCart.objects.filter(recipe=recipe, user=self.request.user)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path='download_shopping_cart', methods=['get',])
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy_list = RecipesIngredient.objects.filter(recipe__in=recipes).values('ingredient').annotate(amount=Sum('amount'))
        tt = f'purchase list for {request.user.username} \n'
        for i in buy_list:
            ingredient_id = i.get('ingredient')
            amount = i.get('amount')
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            tt += f'{ingredient.name} - {amount} {ingredient.measurement_unit} \n'
        recipei = [item.recipe.name for item in shopping_cart]
        tt += 'recipes:'
        for i in recipei:
            tt += f'{i}'
        response = HttpResponse(tt, content_type='text.txt')
        response['Content-Disposition'] = 'attachment; filename="ttt.txt"'
        return response


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = ListCustomUserSerializer

    @action(detail=True, url_path='subscribe', methods=['post', 'delete'])
    def subscribe(self, request, id):
        following = CustomUser.objects.get(pk=id)
        if request.method == 'POST':
            follow = Subscribtion.objects.create(follower=request.user, following=following)
            serializer = SubSerializer(follow, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        sub = Subscribtion.objects.filter(following=following, follower=request.user)
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def shopping_cart(request):
    shopping_cart = ShoppingCart.objects.filter(user=request.user)
    serializer = ShoppingCartSerializer(shopping_cart, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def rt(request):
    rt = RecipesIngredient.objects.filter(recipe=1)
    serializer = rIngredientRecipeSerializer(rt, many=True)
    return Response(serializer.data)