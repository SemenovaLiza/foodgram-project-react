from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from recipes.models import Tag, Ingredient, Recipe


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    pass


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
