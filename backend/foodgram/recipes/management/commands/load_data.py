from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag

file_path = f'{settings.BASE_DIR}/data/'


class Command(BaseCommand):
    def handle(self, *args, **options):
        for row in DictReader(open(file_path + 'tags.csv')):
            tag = Tag(name=row['name'], color=row['color'], slug=row['slug'])
            tag.save()
        for row in DictReader(open(file_path + 'ingredients.csv')):
            ing = Ingredient(
                name=row['name'], measurement_unit=row['measurement_unit']
            )
            ing.save()
