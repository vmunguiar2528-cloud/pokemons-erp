"""Punto de entrada compatible para servicios configurados como gunicorn app:app."""

from core.wsgi import application as app

__all__ = ("app",)
