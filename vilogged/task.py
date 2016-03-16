__author__ = 'musa'
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PARENT = os.path.dirname(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)
virtual_env = os.path.join(PROJECT_ROOT, 'env')
activate_this = os.path.join(virtual_env, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
os.environ["DJANGO_SETTINGS_MODULE"] = 'core.settings'
import django
django.setup()

from utility.utility import Cron
from datetime import datetime
from vilogged.models import Appointments
def run_cron():
    from vilogged.models import Appointments
    return Appointments().set_expired()


from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=8)
def update_expired():
    Appointments().set_expired()

sched.start()