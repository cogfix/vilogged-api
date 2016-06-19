from django.db import models
from datetime import date, datetime
from vilogged.entrance.models import Entrance
from vilogged.users.models import UserProfile
from vilogged.visitors.models import Visitors
from utility.utility import ModelInstanceManager, Utility, json_encoder
import json


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
    is_removed = models.BooleanField(default=False)
    objects = ModelInstanceManager()

    class Meta:
        app_label = 'appointments'

    def __unicode__(self):
        return '{}'.format(self._id)

    def get_status (self, item):
        today = date.today()
        item_date = datetime.strptime(item['start_date'] , '%Y-%m-%d').date()
        if item['is_expired']:
            return self.EXPIRED
        if item['is_approved'] and today <= item_date:
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
        if item['is_approved'] and today > item_date:
            self.set_expired()
            return self.EXPIRED

    def get_team_members(self):
        teams = []
        if self.teams:
            import ast
            teams_members = ast.literal_eval(self.teams)
            for visitor_id in teams_members:
                try:
                    visitor = Visitors.objects.get(_id=visitor_id)
                    teams.append(dict(
                        _id=visitor._id,
                        last_name=visitor.last_name,
                        first_name=visitor.first_name,
                        phone=visitor.phone
                    ))
                except Visitors.DoesNotExist as e:
                    pass

        return teams

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            visitor=self.visitor.to_json(all_fields),
            host=self.host.to_json(all_fields),
            representing=self.representing,
            purpose=self.purpose,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
            start_time=self.start_time.isoformat(),
            end_time=self.end_time.isoformat(),
            escort_required=self.escort_required,
            is_approved=self.is_approved,
            is_expired=self.is_expired,
            is_removed=self.is_removed,
            teams=self.get_team_members(),
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

                if appointment_date < today:
                    appointment.is_expired = True
                    appointment.save()

    @classmethod
    def set_upcoming(cls):
        expired_appointments = Appointments.objects.filter(is_expired=True)
        if len(expired_appointments) > 0:
            today = date.today()
            for appointment in expired_appointments:
                appointment_date = appointment.end_date
                if appointment.end_date >= today:
                    appointment_date = today

                if appointment_date >= today:
                    appointment.is_expired = False
                    appointment.save()

    @classmethod
    def send_notifications(cls):
        upcoming_appointments = Appointments.objects.filter(is_expired=False)





class AppointmentLogs(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment = models.CharField(max_length=50, blank=True, null=True)
    checked_in = models.DateTimeField(default=None, blank=True, null=True)
    checked_out = models.DateTimeField(blank=True, null=True)
    label_code = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_removed = models.BooleanField(default=False)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='log_modified_by')

    class Meta:
        app_label = 'appointments'

    def __unicode__(self):
        return '{}'.format(self.appointment)

    def get_logs(self, appointment_id):
        rlogs = AppointmentLogs.objects.filter(appointment=appointment_id)
        logs = []
        if len(rlogs) > 0:
            for log in rlogs:
                logs.append(log.to_json())
        return logs

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
