from django.core.exceptions import ValidationError


def validate_ingredient_number(value):
    if value < 1:
        raise ValidationError(
            'Количество необходимого ингридиента'
            'должно быть больше 1.'
        )
    return value
