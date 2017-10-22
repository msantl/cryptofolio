#! /bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --no-post-process --noinput
