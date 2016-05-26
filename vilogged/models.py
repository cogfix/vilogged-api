from django.db import models
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import uuid
from django.db.models import Lookup
from vilogged.appointments.models import Appointments, AppointmentLogs
from vilogged.users.models import UserProfile
import json
from utility.utility import Utility
from django.db.models.fields import DateField, DateTimeField, TimeField

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

    def to_json(self, all_fields=False):

        json_object = dict(
                _id=self._id,
                _rev=self._rev,
                message_body=self.message_body,
                destination=self.destination,
                status=self.status,
                type=self.type,
                source=self.source,
                created=Utility.format_datetime(self.created),
                modified=Utility.format_datetime(self.modified),
                created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
                modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object


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

    def to_json(self, all_fields=False):

        json_object = dict(
                _id=self._id,
                _rev=self._rev,
                type=self.type,
                name=self.name,
                code=self.code,
                appointment_id=self.appointment_id,
                source=self.source,
                created=Utility.format_datetime(self.created),
                modified=Utility.format_datetime(self.modified),
                created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
                modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object

    def get_appointment(self):
        appointment_data = {}
        if self.appointment_id:
            appointment_data = self.appointment_id.to_json(False)
        return appointment_data


class Changes(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    model = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    row_id = models.CharField(max_length=20)
    rev = models.CharField(max_length=100, blank=True, null=True)
    snapshot = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def to_json(self, all_fields=False):

        json_object = dict(
                _id=self._id,
                _rev=self._rev,
                model=self.model,
                type=self.type,
                row_id=self.row_id,
                rev=self.rev,
                snapshot=self.snapshot,
                reviewed=self.reviewed,
                created=Utility.format_datetime(self.created)
        )

        if all_fields:
            json_object.update(dict())

        return json_object

from visitors.models import Visitors, VisitorGroup
from company.models import Company
from department.models import Department
from entrance.models import Entrance

@receiver(pre_save)
def update_id(sender, instance=None, **kwargs):
    def save_snapshot(sender, instance, **kwargs):
        def get_value(data, field):
            from django.db.models.fields.related import ForeignKey
            if isinstance(field, ForeignKey) and data:
                return getattr(data, '_id', 'no id')
            elif data is not None:
                return data
            elif isinstance(field, (DateTimeField, DateField, TimeField)):
                return Utility.format_datetime(data)
            else:
                return ''
        if getattr(instance, '_id', None) is not None:
            changed = dict()
            current_record = sender.objects.filter(_id=instance._id)
            if len(current_record) > 0:
                current_record = current_record.first()
                fields = instance._meta.get_fields()
                for field in fields:
                    if field.name not in ['modified_by', 'created_by', '_rev', 'logentry', 'password']:
                        try:
                            current_value = getattr(current_record, field.name)
                            instance_value = getattr(instance, field.name)
                            if current_value != instance_value:
                                if instance(field, DateField):
                                    current_value = Utility.format_datetime(current_value)
                                changed[field.name] = get_value(current_value, field)
                        except:
                            pass

            if len(changed) > 0:
                model = sender.__name__.lower()
                try:
                    Changes.objects.create(model=model, type='updated', row_id=instance._id, snapshot=json.dumps(changed))
                except Exception as e:
                    print (changed)


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
    if sender.__name__ in list_of_models and sender.__name__ != 'Changes':
        save_snapshot(sender, instance, **kwargs)


@receiver(post_save)
def manage_post(sender, instance=None, created=False, **kwargs):

    ''' Creates a token whenever a User is created '''
    if created and sender.__name__ is 'UserProfile':
        try:
            Token.objects.create(user=instance)
        except:
            pass

    model = sender.__name__.lower()
    if model != 'changes' and sender.__name__ in list_of_models:

        pre_saved = Changes.objects.filter(reviewed=False, model=model, row_id=instance._id)
        if len(pre_saved) > 0:
            pre_saved = pre_saved.first()
            pre_saved.reviewed = True
            pre_saved.save()
        else:
            if created:
                type = 'created'
                snapshot = serialize_model_instance(instance)
            else:
                type = 'updated'
                snapshot = dict()
            Changes.objects.create(model=model, type=type, row_id=instance._id, reviewed=True, rev=instance._rev, snapshot=json.dumps(snapshot))

@receiver(post_delete)
def manage_delete(sender, instance=None, using=None, **kwargs):

    ''' Creates a token whenever a User is created '''
    try:
        model = sender.__name__.lower()
        type = 'delete'
        if model != 'changes' and sender.__name__ in list_of_models:
            snapshot = json.dumps(serialize_model_instance(instance))
            Changes.objects.create(model=model, type=type, row_id=instance._id, snapshot=snapshot, rev=instance._rev)
    except:
        pass



def serialize_model_instance(instance):
    def get_value(data, field):
        from django.db.models.fields.related import ForeignKey
        if isinstance(field, ForeignKey) and data:
            return getattr(data, '_id', 'no id')
        elif data is not None:
            return data
        else:
            return ''
    fields = instance._meta.get_fields()
    serialized_instance = dict()
    for field in fields:
        if field.name not in ['logentry', 'password']:
            try:
                instance_value = getattr(instance, field.name)
                serialized_instance[field.name] = str(get_value(instance_value, field))
            except AttributeError:
                pass
    return serialized_instance