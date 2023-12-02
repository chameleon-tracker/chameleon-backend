from django.db import models

__all__ = ["MarkupLanguages"]


class MarkupLanguages(models.TextChoices):
    """Known markup languages."""

    PLAIN = "PLAIN", "Plain text"
    MARKDOWN = "MARKDOWN", "Markdown"
    ASCIIDOC = "ASCIIDOC", "AsciiDoc"
