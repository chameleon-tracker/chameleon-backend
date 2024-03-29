# Generated by Django 5.0 on 2024-01-15 13:29

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("chameleon_project_project", "0002_chameleonprojecthistory"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChameleonTicketHistory",
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
                ("object_id", models.BigIntegerField()),
                ("timestamp", models.DateTimeField()),
                (
                    "action",
                    models.CharField(help_text="History action", max_length=255),
                ),
                ("field", models.TextField(null=True)),
                ("value_from", models.TextField(blank=True, null=True)),
                ("value_to", models.TextField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
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
                ("title", models.CharField(help_text="Ticket title", max_length=200)),
                (
                    "creation_time",
                    models.DateTimeField(help_text="When ticket has been created"),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="chameleon_project_project.chameleonproject",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
