#!/bin/bash

python manage.py syncdb --noinput
python manage.py migrate scores 0001_initial --fake
python manage.py migrate scores
