import typing
from collections import abc

from django.db.models import enums
from django.db.models import fields

from chameleon.common.enums import MarkupLanguages

__all__ = ["choice_field", "markup_field"]

Choices = typing.TypeVar("Choices", bound=enums.Choices)


def set_kwargs_value(target: abc.MutableMapping[str, typing.Any], **kwargs):
    """Set value with validation that this value isn't specified twice.

    Args:
        target:
        **kwargs:

    Returns:

    """
    for key, value in kwargs.items():
        if key in target and value is not None:
            raise ValueError(f"'{key}' has been specified twice")

        if value is not None:
            target[key] = value


def set_kwargs_default(target: abc.MutableMapping[str, typing.Any], **kwargs):
    """Set value if it isn't already defined."""
    for key, value in kwargs.items():
        if key not in target:
            target[key] = value


def choice_field(
    enumeration: type[Choices],
    default: Choices | None = None,
    help_text: str | None = None,
    /,
    *,
    field_type: type[fields.Field] = fields.CharField,
    **kwargs,
) -> fields.Field:
    """Generate an enumeration field with some default attributes.

    Main goal is minimization code duplication and inconsistency.

    Args:
        enumeration: Enumeration to specify for a field.
        default: Default version for given enumeration field.
        help_text: Documentation text for a field.
        field_type: Database field type.
        **kwargs: Additional arguments for field type constructor.

    Returns:

    """
    set_kwargs_value(
        kwargs,
        choices=enumeration.choices,
        help_text=help_text,
        default=default,
    )

    if field_type is fields.CharField:
        set_kwargs_default(kwargs, max_length=255)

    return field_type(**kwargs)


def markup_field(model_field: str | None = None) -> fields.Field:
    """Generate choice field for markup language.

    Args:
        model_field: text representation of the field used for help text

    Returns: Field

    """
    if model_field:
        help_text = f"{model_field} markup language"
    else:
        help_text = None

    return choice_field(
        MarkupLanguages,
        MarkupLanguages.PLAIN,
        help_text,
    )
