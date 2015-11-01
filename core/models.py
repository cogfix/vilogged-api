from django.db import models
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import uuid
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Lookup

list_of_models = (
    'UserProfile',
    'Department',
    'Vehicles',
    'Entrance',
    'VisitorGroup',
    'Company',
    'Visitors',
    'Appointments',
    'AppointmentLogs',
    'MessageQueue',
    'Changes',
    'RestrictedItems',
)

class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

from django.db.models.fields import Field
Field.register_lookup(NotEqual)

# Create your models here.

class Department(models.Model):
    _id = models.CharField(max_length=100, unique=True,  primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    floor = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.name)


class UserProfile(AbstractUser, models.Model):
    _id = models.CharField(max_length=100,  unique=True,  primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    gender = models.CharField(max_length=10, default='Male')
    phone = models.CharField(max_length=20, unique=True)
    home_phone = models.CharField(max_length=20, blank=True, null=True)
    work_phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.username)

    def clean(self):
        if self.first_name is None:
            raise ValidationError(_('Draft entries may not have a publication date.'))


class Entrance(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.name)


class VisitorGroup(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    black_listed = models.BooleanField(default=False)
    params = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{0}'.format(self.name)


class Company(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='co_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='co_modified_by')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{0}'.format(self.name)


class Visitors(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=7, default='Male')
    phone = models.CharField(max_length=20, unique=True, verbose_name='visitors phone number')
    occupation = models.CharField(max_length=50, blank=True, null=True)
    company = models.ForeignKey(Company, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=20, blank=True, null=True)
    state_of_origin = models.CharField(max_length=50, blank=True, null=True)
    lga_of_origin = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    fingerprint = models.TextField(blank=True, null=True)
    signature = models.TextField(blank=True, null=True)
    pass_code = models.CharField(max_length=50, blank=True, null=True)
    group = models.ForeignKey(VisitorGroup, related_name='group', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='modified_by')

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Appointments(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    visitor = models.ForeignKey(Visitors, related_name="visitor")
    host = models.ForeignKey(UserProfile, blank=True, null=True, related_name="host")
    representing = models.CharField(max_length=100, blank=True, null=True)
    purpose = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    escort_required = models.BooleanField(default=False)
    is_approved = models.NullBooleanField(default=None, null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    teams = models.TextField(null=True, blank=True)
    entrance = models.ForeignKey(Entrance, blank=True, null=True, related_name="entrance")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='app_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='app_modified_by')


class Vehicles(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment_id = models.ForeignKey(Appointments, blank=True, null=True, related_name='vehicle')
    license = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(blank=True, null=True, max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='ve_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='ve_modified_by')


class MessageQueue(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    message_body = models.TextField()
    destination = models.CharField(max_length=50)
    source = models.CharField(max_length=50)
    subject = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='me_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='me_modified_by')


class RestrictedItems(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    appointment_id = models.ForeignKey(Appointments, blank=True, null=True, related_name="restricted_items")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='re_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='re_modified_by')

class AppointmentLogs(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment = models.ForeignKey(Appointments)
    checked_in = models.DateTimeField(default=None, blank=True, null=True)
    checked_out = models.DateTimeField(blank=True, null=True)
    label_code = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_modified_by')


class Changes(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    model = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    row_id = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)


@receiver(pre_save)
def update_id(sender, instance=None, **kwargs):

    if sender.__name__ in list_of_models: # this is the dynamic
        if instance._id is None or instance._id == '':
            instance._id = '{}'.format(uuid.uuid4()).replace('-', '')

        if instance._rev is None or instance._rev == '':
            rev = '{}'.format(uuid.uuid4()).replace('-', '')
            instance._rev = '1-{}'.format(rev)
        else:
            count = instance._rev.split('-')
            count = int(count[0]) + 1
            new_rev = '{}'.format(uuid.uuid4()).replace('-', '')
            instance._rev = '{0}-{1}'.format(count, new_rev)


@receiver(post_save)
def manage_post(sender, instance=None, created=False, **kwargs):

    ''' Creates a token whenever a User is created '''
    if created and sender.__name__ is 'UserProfile':
        try:
            Token.objects.create(user=instance)
        except:
            pass

    try:
        model = sender.__name__.lower()
        if created:
            type = 'created'
        else:
            type = 'updated'
        if model != 'changes' and sender.__name__ in list_of_models:
            Changes.objects.create(model=model, type=type, row_id=instance._id)
    except:
        pass
@receiver(post_delete)
def manage_delete(sender, instance=None, using=None, **kwargs):

    ''' Creates a token whenever a User is created '''
    try:
        model = sender.__name__.lower()
        type = 'delete'
        if model != 'changes' and sender.__name__ in list_of_models:
            Changes.objects.create(model=model, type=type, row_id=instance._id)
    except:
        pass