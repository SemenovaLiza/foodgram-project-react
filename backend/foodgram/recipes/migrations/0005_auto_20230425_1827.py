# Generated by Django 3.2 on 2023-04-25 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230423_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipesingredient',
            name='amount',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes_images/', verbose_name='Изображение рецепта'),
        ),
    ]
