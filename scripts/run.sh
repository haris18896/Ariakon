   #!/bin/sh

   set -e

   # Wait for the database to be ready
   python manage.py wait_for_db

   # Collect static files
   python manage.py collectstatic --noinput

   # Run migrations
   python manage.py migrate

   # Start uWSGI server
   uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi