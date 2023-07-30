from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, SubscribeViewSet,
                    TagViewSet, download_shopping_cart)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('recipes/<int:id>/shopping_cart/',
         ShoppingCartViewSet.as_view(),
         name='shopping_cart'),
    path('recipes/<int:id>/favorite/',
         FavoriteViewSet.as_view(),
         name='favorite'),
    path(
        'users/<int:id>/subscribe/',
        SubscribeViewSet.as_view(),
        name='subscribe'
    ),
    path(
        'recipes/<int:id>/download_shopping_cart/',
        download_shopping_cart,
        name='subscribe'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls'))
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
