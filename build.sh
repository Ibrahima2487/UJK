#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py tailwind build
pyton manage.py tailwind start
python manage.py collectstatic --no-input
python manage.py migrate