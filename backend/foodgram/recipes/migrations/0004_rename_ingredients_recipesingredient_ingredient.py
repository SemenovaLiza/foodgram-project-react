# Generated by Django 3.2 on 2023-05-07 18:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_recipesingredient_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipesingredient',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]
