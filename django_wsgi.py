import os
import sys
import  django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'cmdb.settings'
#application=django.core.handlers.wsgi.WSGIHandler()

from django.core.wsgi import get_wsgi_application  
application = get_wsgi_application()  
