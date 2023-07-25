from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipesIngredient,
                     ShoppingCart, Tag, RecipesTag)


class TagsInLine(admin.TabularInline):
    model = RecipesTag
    rows = 4


class IngredientsInLine(admin.TabularInline):
    model = RecipesIngredient
    rows = 5


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    empty_value_display = '-пусто-'
    inlines = (IngredientsInLine, TagsInLine)

    def favorites(self, obj):
        if Favorite.objects.filter(recipe=obj).exists():
            return Favorite.objects.filter(recipe=obj).count()
        else:
            return 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')
    empty_value_display = '-пусто-'
