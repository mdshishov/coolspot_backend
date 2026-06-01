import re

from django.core.exceptions import ValidationError


def validate_client_name(value):
    name_pattern = re.compile(
        r"^[A-Za-zА-Яа-яЁё]+"
        r"(?:-[A-Za-zА-Яа-яЁё]+)?"
        r"(?: [A-Za-zА-Яа-яЁё]+"
        r"(?:-[A-Za-zА-Яа-яЁё]+)?){0,2}$"
    )
    if not name_pattern.fullmatch(value):
        raise ValidationError("Некорректное значение")