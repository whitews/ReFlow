"""
WSGI config for reflow project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys

# Set matplotlib configuration directory, else Django complains it is not writable
# We'll just use a tempfile
import tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

paths = [
    '/srv/django-projects/ReFlow',
    '/srv/django-projects/ReFlow/reflow'
]

for path in paths:
    if path not in sys.path:
        sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reflow.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application

import settings

if settings.INTERACTIVE_DEBUG:
    class Debugger:

        def __init__(self, object):
            self.__object = object

        def __call__(self, *args, **kwargs):
            import pdb
            debugger = pdb.Pdb()
            debugger.use_rawinput = 0
            debugger.reset()
            sys.settrace(debugger.trace_dispatch)

            try:
                return self.__object(*args, **kwargs)
            finally:
                debugger.quitting = 1
            sys.settrace(None)

    application = Debugger(get_wsgi_application())
else:
    application = get_wsgi_application()
