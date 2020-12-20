release: python manage.py migrate
web: gunicorn warzone_general.wsgi
worker: python manage.py process_tasks