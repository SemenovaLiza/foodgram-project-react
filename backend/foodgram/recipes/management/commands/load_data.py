from django.core.management.base import BaseCommand
import json
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Load JSON ingredients and tags data'

    def handle(self, *args, **options):
        with open('data/ingredients.json') as ingredients_data:
            ingredients = json.load(ingredients_data)
        for ingredient in ingredients:
            Ingredient.objects.get_or_create(**ingredient)

        with open('data/tags.json') as tags_data:
            tags = json.load(tags_data)
        for tag in tags:
            Tag.objects.get_or_create(**tag)
