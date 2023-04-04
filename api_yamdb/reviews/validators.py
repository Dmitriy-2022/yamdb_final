import datetime

from django.core.exceptions import ValidationError


def validate_year(value):
    if value > datetime.datetime.now().year:
        raise ValidationError(
            f'Год выпуска {value} больше текущего'
        )
