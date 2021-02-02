# Deployment steps to heroku

https://www.youtube.com/watch?v=GMbVzl_aLxM


# Dump data to a json file

python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > dump.json

# Load dumped data to db

python manage.py loaddata dump.json