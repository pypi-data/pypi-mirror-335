from pathlib import PurePosixPath

from django.core.exceptions import ValidationError
from django.core.validators import (
    BaseValidator,
    DecimalValidator,
    EmailValidator,
    FileExtensionValidator,
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    ProhibitNullCharactersValidator,
    RegexValidator,
)
from django.utils.translation import gettext_lazy as _


class IncreasingRangeValidator(BaseValidator):
    message = _(
        "Ending value in range must be greater "
        + "than or equal to the starting value ({range})"
    )
    code = "increasing_range"

    def __init__(self):
        super().__init__(0)

    def compare(self, a, b):
        if a.lower > a.upper:
            params = {range: f"{a.lower}-{a.upper}"}
            raise ValidationError(message=self.message, code=self.code, params=params)
        return False


class RangeValidator(BaseValidator):
    def __init__(self, validator: BaseValidator):
        self._validator = validator

    def __call__(self, value):
        # TODO: separate error messages (add `lower`/`upper``)
        self._validator(value.lower)
        self._validator(value.upper)


class ArrayValueValidator(BaseValidator):
    def __init__(self, validator: BaseValidator):
        self._validator = validator

    def __call__(self, value):
        # TODO: separate error messages (add index)
        for val in value:
            self._validator(val)


class FilePathValidator(BaseValidator):
    message = _("Invalid file path (%(show_value)s). It must be an absolute posix path")
    code = "invalid_file_path"

    def __init__(self):
        super().__init__(0)

    def compare(self, a, b):
        return not PurePosixPath(a).is_absolute()
