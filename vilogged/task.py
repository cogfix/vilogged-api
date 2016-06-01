__author__ = 'musa'
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
ENV_PATH = os.path.join(PROJECT_ROOT, 'env')
sys.path.insert(0, PROJECT_ROOT)
if os.path.isdir(ENV_PATH):
    virtual_env = ENV_PATH
    activate_this = os.path.join(virtual_env, 'bin/activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))
os.environ["DJANGO_SETTINGS_MODULE"] = 'vilogged.settings'
import django
django.setup()

from datetime import datetime
from vilogged.models import Appointments
in_progress = dict(
    expired=False,
    upcoming=False
)
def update_expired():
    global in_progress
    if not in_progress['expired']:
        in_progress['expired'] = True
        Appointments().set_expired()
        in_progress['expired'] = False

def update_upcoming():
    global in_progress
    if not in_progress['upcoming']:
        in_progress['upcoming'] = True
        Appointments().set_upcoming()
        in_progress['upcoming'] = False

def send_notifications():
    Appointments().send_notifications()

import time
import schedule

schedule.every(60).seconds.do(send_notifications)
schedule.every(60).seconds.do(update_expired)
schedule.every(300).seconds.do(update_upcoming)

try:
    while 1:
        schedule.run_pending()
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    pass