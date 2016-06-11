__author__ = 'musa'
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)
virtual_env = os.path.join(PROJECT_ROOT, 'env')
activate_this = os.path.join(virtual_env, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
os.environ["DJANGO_SETTINGS_MODULE"] = 'vilogged.settings'
import django
django.setup()

from vilogged.users.models import UserProfile

print (UserProfile.objects.get(username='admin'))


