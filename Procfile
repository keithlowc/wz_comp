worker: chmod 777 -R ./release-tasks.sh
release: ./release-tasks.sh
web: gunicorn warzone_general.wsgi
worker: python manage.py process_tasks