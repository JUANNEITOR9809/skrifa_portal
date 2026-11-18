#!/usr/bin/env bash
# Render ejecuta este archivo al construir la aplicación.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
