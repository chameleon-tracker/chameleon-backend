# Generated by Django 4.2.6 on 2023-10-28 13:32

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("chameleon_project_project", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChameleonTicket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "description_markup",
                    models.CharField(
                        choices=[
                            ("Plain text", "Plain"),
                            ("Markdown", "Markdown"),
                            ("AsciiDoc", "Asciidoc"),
                        ],
                        default="Plain text",
                        help_text="Project issue description markup language",
                        max_length=255,
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="chameleon_project_project.chameleonproject",
                    ),
                ),
            ],
        ),
    ]
