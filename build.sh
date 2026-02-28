#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Static files collect karein (Iske liye settings mein STATIC_ROOT hona zaroori hai)
python manage.py collectstatic --no-input

# Database migrate karein
python manage.py migrate