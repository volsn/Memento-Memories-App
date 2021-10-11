# Memento 

Memento: an app to keep track of your on-the-spot thoughts and ideas.


Technologies used in this Project:

- Django
- Django Signals
- Django Rest Framework
- PostgreSQL
- Celery
- Redis
- Docker-Compose
- Flake8
- Jenkins
- Postman

___
## Run

Run with docker-compose

```bash
$ docker-compose up --build
```

___
## Populate

App includes special manage command for populating database with fake data
```bash
$ docker-compose exec app sh -c "python manage.py populate"
```

___
## Testing and Linting

The project also comes with tests covering core functionality of the app.

These can be run together with linter via following command
```bash
$ docker-compose exec app sh -c "python manage.py test --settings=settings.test && flake8"
```
