from django.db import models
from user_profile.models import UserProfile, Department
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import uuid
from datetime import date
from django.db.models import Lookup
class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params

from django.db.models.fields import Field
Field.register_lookup(NotEqual)

@receiver(pre_save)
def update_id(sender, instance=None, **kwargs):
    list_of_models = (
        'UserProfile',
        'Department',
        'Vehicles',
        'Entrance',
        'VisitorGroup',
        'Company',
        'Visitors',
        'Appointments',
        'MessageQueue',
        'RestrictedItems',
    )
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




@receiver(post_save, sender=UserProfile)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    ''' Creates a token whenever a User is created '''
    if created:
        try:
            Token.objects.create(user=instance)
        except:
            pass


# Create your models here.

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
    is_approved = models.IntegerField(default=None, null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    checked_in = models.DateTimeField(default=None, blank=True, null=True)
    checked_out = models.DateTimeField(blank=True, null=True)
    label_code = models.CharField(max_length=50, null=True, blank=True)
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