web: mkdir frontend/build && wget "https://nightly.link/Snowdays23/full-website-frontend/workflows/main/internal-form/artifact.zip" -O frontend/build/built.zip && cd frontend/build && unzip built.zip && cd ../.. && python manage.py makemigrations && python manage.py migrate --run-syncdb && python manage.py collectstatic && gunicorn snowdays23.wsgi
