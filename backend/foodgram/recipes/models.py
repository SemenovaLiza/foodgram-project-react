from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from .validators import validate_ingredient_number

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название тега'
        )
    color = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=250,
        unique=True,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=150,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
        )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes_images',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipesIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='ingredients'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipesIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        validators=[validate_ingredient_number],
        verbose_name='Количество необходимого ингридиента'
    )
