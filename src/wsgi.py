"""
WSGI entrypoint for running the Dash app with a production server (Gunicorn).

Usage (from project root):
  gunicorn -b 0.0.0.0:8050 src.wsgi:server --workers 2 --threads 2 --timeout 120

This file exposes `server`, a Flask WSGI application that wraps the Dash app.
"""
from .dashboard import create_app

# Build the Dash app
_dash_app = create_app()

# Expose Flask server for Gunicorn
server = _dash_app.server
