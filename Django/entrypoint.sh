#!/bin/bash
set -e

# 1) DB ready
# ./wait-for-it.sh "$DATABASE_HOST:$DATABASE_PORT" -t 60

# 2) migrate（毎回OK・冪等）
python manage.py migrate --noinput

# 3) superuser（ないときだけ作成）
python - <<'PY'
import os
from django.contrib.auth import get_user_model
import django
django.setup()
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    u = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    e = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    p = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpass")
    User.objects.create_superuser(u, e, p)
PY

# 4) static
# python manage.py collectstatic --noinput

# 5) start server
gunicorn core.wsgi:application --bind 0.0.0.0:8000