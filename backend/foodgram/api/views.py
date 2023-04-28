from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.response import Response


from .serializers import TagSerializer, AddRecipeSerializer, ListRecipeSerializer, FavoriteSerializer
from recipes.models import Tag, Recipe, Favorite


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
