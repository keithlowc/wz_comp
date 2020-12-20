release: chmod +x release-tasks.sh && ./release-tasks.sh
web: gunicorn warzone_general.wsgi
worker: python manage.py process_tasks