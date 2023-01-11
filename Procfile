web: cd frontend && npm install && npm run build && cd .. && python manage.py makemigrations && python manage.py migrate --run-syncdb && python manage.py collectstatic && gunicorn snowdays23.wsgi
