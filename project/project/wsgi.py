"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

project_home = os.path.expanduser('~/project')

if project_home not in sys.path:
    sys.path.insert(0, project_home)

activate_this = os.path.expanduser('~/virtenv/bin/activate_this.py')

with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()