"""Конфигурация приложения статических страниц."""
from django.apps import AppConfig


class PagesConfig(AppConfig):
    """Конфигурация приложения статических страниц."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pages'
