from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .pagination import Pagination


class PostDeleteMixin:
    """Миксин для создания и удаления объекта из базы данных."""
    permission_classes = [IsAuthenticated, ]
    pagination_class = Pagination
    model_class = None
    serializer_class = None
    obj_model = None
    object_name = 'recipe'

    def post(self, request, id):
        obj = get_object_or_404(
            self.obj_model, pk=id
        )
        data = {
            self.object_name: obj.id,
            'user': request.user.id
        }
        serializer = self.serializer_class(
            data=data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        obj = get_object_or_404(
            self.obj_model, pk=id
        )
        query_param = {
            self.object_name: obj,
            'user': request.user
        }
        data = self.model_class.objects.filter(**query_param)
        data.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
