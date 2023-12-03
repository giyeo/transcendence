python manage.py collectstatic --noinput
gunicorn transcendence.wsgi:application --bind 0.0.0.0:8000 &
daphne -b 0.0.0.0 -p 8001 transcendence.asgi:application &
tail -f /dev/null