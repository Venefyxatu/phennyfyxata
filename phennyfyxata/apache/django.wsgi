import os
import sys

sys.path.append('/var/www/venefyxatu.be/phenny')

os.environ['DJANGO_SETTINGS_MODULE'] = 'phennyfyxata.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
