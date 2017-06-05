"""
WSGI config for RE_bot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
from django.db import connection

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

connection.connection.text_factory = str

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RE_bot.settings")

application = get_wsgi_application()
