#!/usr/bin/env bash

python manage.py migrate
python manage.py collectstatic
python manage.py pre_release_tasks