from django.db import models
from utility.utility import Utility


class Entrance(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)
    is_removed = models.BooleanField(default=False)

    class Meta:
        app_label = 'entrance'

    def __unicode__(self):
        return '{}'.format(self.name)

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            name=self.name,
            created=Utility.format_datetime(self.created),
            modified=Utility.format_datetime(self.modified),
            created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
            modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object
