from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.settings import NAME_MAX_LENGTH, RECIPE_MAX_LENGTH
from users.models import CustomUser


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название тега'
        )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=NAME_MAX_LENGTH,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
        )
    name = models.CharField(
        max_length=RECIPE_MAX_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes_images/',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipesTag',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipesIngredient',
        verbose_name='Ингредиенты'
    )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000)
        ],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.author} - {self.name}({self.tags})'

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipesIngredient(models.Model):
    """Модель, связывающая рецепт с
    указанными в нем ингредиентами.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredientsinrecipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class RecipesTag(models.Model):
    """Модель, связывающая рецепт с тегами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.recipe}: {self.tag}'

    class Meta:
        verbose_name = 'Тег, к которому относится рецепт'
        verbose_name_plural = 'Теги, к которым относится рецепт'


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    def ___str__(self):
        return f'{self.user}: {self.recipe}'

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    """Модель корзины с рецептами."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    def ___str__(self):
        return f'{self.user}: {self.recipe}'

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
