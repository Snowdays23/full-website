web: mkdir frontend/build && curl $(curl -s https://api.github.com/repos/Snowdays23/full-website-frontend/actions/artifacts\?per_page\=1 | jq '[.artifacts[] | {name : .name, archive_download_url : .archive_download_url}]' | jq -r '.[] | select (.name == "artifact") | .archive_download_url') --output frontend/build/built.zip && cd frontend/build && unzip built.zip && cd ../.. && python manage.py makemigrations && python manage.py migrate --run-syncdb && python manage.py collectstatic && gunicorn snowdays23.wsgi
