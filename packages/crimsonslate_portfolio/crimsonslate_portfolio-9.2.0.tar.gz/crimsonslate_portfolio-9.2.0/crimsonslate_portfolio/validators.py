import emoji as e

from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import (
    FileExtensionValidator,
    get_available_image_extensions,
)
from django.utils.translation import gettext_lazy as _


def validate_media_file_extension(value: File) -> None:
    video_extensions: list[str] = ["mp4"]
    image_extensions: list[str] = list(get_available_image_extensions())
    validator = FileExtensionValidator(
        allowed_extensions=[
            file_extension for file_extension in video_extensions + image_extensions
        ]
    )
    validator(value)
    return


def validate_emoji(value: str) -> None:
    if not e.is_emoji(e.emojize(value, language="alias")):
        raise ValidationError(
            _("'%(value)s' ain't an emoji."),
            code="invalid",
            params={"value": value},
        )
