# Ariakon 

### Delete all the migration files:
* Remove all migration files (except __init__.py) from your core and any other app directories, such as admin, to ensure a fresh migration setup.

```sh
$ find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
$ docker-compose run --rm app sh -c "python manage.py makemigrations"
$ docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
```