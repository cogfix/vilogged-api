from django.db import models
from vilogged.users.models import UserProfile
from utility.utility import Utility


class Company(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    address = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='co_created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='co_modified_by')
    is_removed = models.BooleanField(default=False)

    class Meta:
        app_label = 'company'

    def __unicode__(self):
        return '{0}'.format(self.name)

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            name=self.name,
            address=self.address,
            created=Utility.format_datetime(self.created),
            modified=Utility.format_datetime(self.modified),
            created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
            modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object
