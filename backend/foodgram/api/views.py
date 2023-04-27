from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


from .serializers import TagSerializer, AddRecipeSerializer, ListRecipeSerializer
from recipes.models import Tag, Recipe


class ListRetrieveViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    pass


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
