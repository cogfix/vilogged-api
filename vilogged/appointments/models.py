from django.db import models
from datetime import date, datetime
from vilogged.entrance.models import Entrance
from vilogged.users.models import UserProfile
from vilogged.visitors.models import Visitors
from utility.utility import ModelInstanceManager, Utility, json_encoder


class Appointments(models.Model):
    REJECTED = 0
    UPCOMING = 1
    PENDING = 2
    EXPIRED = 3
    IN_PROGRESS = 4

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
    objects = ModelInstanceManager()

    class Meta:
        app_label = 'appointments'

    def __unicode__(self):
        return '{}'.format(self._id)

    def get_status (self, item):
        today = date.today()
        if item['is_expired']:
            return self.EXPIRED
        if item['is_approved'] and today <= item['start_date']:
            activities = AppointmentLogs.objects.filter(
                    appointment=item['_id'],
                    checked_out=None,
                    checked_in__year=today.year,
                    checked_in__month=today.month,
                    checked_in__day=today.day,
            )
            if len(activities) > 0:
                return self.IN_PROGRESS
            return self.UPCOMING
        if item['is_approved'] is False:
            return self.REJECTED
        if item['is_approved'] is None:
            return self.PENDING

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            visitor=self.visitor.to_json(),
            host=self.host.to_json(),
            representing=self.representing,
            purpose=self.purpose,
            start_date=self.start_time.isoformat(),
            end_date=self.end_date.isoformat(),
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            escort_required=self.escort_required,
            is_approved=self.is_approved,
            is_expired=self.is_expired,
            teams=self.teams,
            entrance=self.entrance,
            created=self.created.isoformat(),
            modified=Utility.format_datetime(self.modified),
            created_by=Utility.return_instance_id(self.created_by),
            modified_by=Utility.return_instance_id(self.modified_by)
        )

        if all_fields:
            json_object.update(dict())

        return json_object

    @classmethod
    def set_expired(cls):

        active_appointment = Appointments.objects.filter(is_expired=False)

        if len(active_appointment) > 0:
            today = date.today()
            for appointment in active_appointment:
                appointment_date = appointment.end_date
                if appointment.end_date >= today:
                    appointment_date = today

                if appointment_date > today:
                    appointment.is_expired = True
                    appointment.save()


class AppointmentLogs(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment = models.CharField(Appointments, max_length=50, blank=True, null=True)
    checked_in = models.DateTimeField(default=None, blank=True, null=True)
    checked_out = models.DateTimeField(blank=True, null=True)
    label_code = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_modified_by')

    class Meta:
        app_label = 'appointments'

    def __unicode__(self):
        return '{}'.format(self.appointment)

    def to_json(self, all_fields=False):

        json_object = dict(
                _id=self._id,
                _rev=self._rev,
                appointment=self.appointment,
                checked_in=Utility.format_datetime(self.checked_in),
                checked_out=Utility.format_datetime(self.checked_out),
                label_code=self.label_code,
                created=Utility.format_datetime(self.created),
                modified=Utility.format_datetime(self.modified),
                created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
                modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object
