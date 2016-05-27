from django.db import models
from vilogged.users.models import UserProfile
from vilogged.appointments.models import Appointments
from utility.utility import ModelInstanceManager, Utility


class Vehicles(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment = models.ForeignKey(Appointments, blank=True, null=True, related_name='vehicle')
    license = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(blank=True, null=True, max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='ve_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='ve_modified_by')
    objects = ModelInstanceManager()

    class Meta:
        app_label = 'vehicles'

    def __unicode__(self):
        return '{}'.format(self.license)

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            appointment=self.get_appointment(all_fields),
            license=self.license,
            model=self.model,
            type=self.type,
            color=self.color,
            created=Utility.format_datetime(self.created),
            modified=Utility.format_datetime(self.modified),
            created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
            modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object

    def get_appointment(self, all_fields=False):

        if self.appointment is not None:
            return self.appointment.to_json(all_fields)
        return self.appointment
