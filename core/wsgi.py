import os
import sys

# Loyiha yo'li
path = '/home/mmuxammadamincom/e-commers'
if path not in sys.path:
    sys.path.append(path)

# Settings faylingiz qayerda joylashgani (core/settings.py bo'lsa 'core.settings')
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
