from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


def validate_image_size(image):
    max_size_mb = 2
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f"Размер изображения не должен превышать {max_size_mb}MB."
        )


image_extension_validator = FileExtensionValidator(
    allowed_extensions=["jpg", "jpeg", "png", "webp"]
)
