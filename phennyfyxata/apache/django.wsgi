import os
import sys

sys.path.append('/RAID/sandbox/django/phennyfyxata')

os.environ['DJANGO_SETTINGS_MODULE'] = 'phennyfyxata.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
