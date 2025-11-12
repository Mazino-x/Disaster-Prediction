"""
WSGI entrypoint for production servers.

Usage examples (gunicorn):
  gunicorn src.api.main:app
  # or with this file:
  gunicorn wsgi:application

This file simply exposes the Flask app as `application` for WSGI servers.
"""
from src.api.main import app

# Some WSGI servers expect `application` as the callable name
application = app
