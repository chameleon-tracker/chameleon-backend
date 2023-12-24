from django.db import models

__all__ = ["MarkupLanguages"]


class MarkupLanguages(models.TextChoices):
    """Known markup languages."""

    PLAIN = "PLAIN"
    MARKDOWN = "MARKDOWN"
    ASCIIDOC = "ASCIIDOC"
