"""Django settings for chameleon project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import importlib.util
import os.path
from collections import abc
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = Path(os.path.curdir).absolute()

SCHEMAS_PATHS_OR_MODULES: abc.Sequence[str | Path] | str | Path

ALLOWED_HOSTS = ["*"]

if importlib.util.find_spec("chameleon.schemas"):
    SCHEMAS_PATHS_OR_MODULES = "module:chameleon.schemas"
else:
    # Dangerous hack to allow dev installation
    local_schemas = Path(os.path.curdir).absolute() / "schemas"
    SCHEMAS_PATHS_OR_MODULES = local_schemas

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-l($%y7)7xxj7v%c=3@^!s9isytkrob&-m56!g!*7bi16!rkgvy"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS = [
    "chameleon.application.json",  # Schema and schema-based things
    "chameleon.project.project",
    "chameleon.project.ticket",
    "chameleon.step.framework.django",
    "django.contrib.contenttypes",
]

ROOT_URLCONF = "chameleon.application.urls"

WSGI_APPLICATION = "chameleon.application.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_DIR / "db.sqlite3",
    }
}

TIME_ZONE = "UTC"

USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# https://code.djangoproject.com/ticket/27238
APPEND_SLASH = False

# Temporary solution to show SQL on console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "verbose": {
            "format": "[django] %(levelname)s %(asctime)s %(module)s"
            " %(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "django": {
            "level": "DEBUG",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
        "propagate": True,
    },
}
