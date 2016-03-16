from django.db import models
from utility.utility import ModelInstanceManager, Utility


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
    objects = ModelInstanceManager()

    class Meta:
        app_label = 'department'

    def __unicode__(self):
        return '{}'.format(self.name)

    @classmethod
    def model_fields(cls):
        return ['name', 'floor', 'description']

    def to_json(self, all_fields=False):
        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            name=self.name,
            floor=self.floor,
            description=self.description,
            created=Utility.format_datetime(self.created),
            modifeid=Utility.format_datetime(self.modified),
            created_by=Utility.return_instance_id(self.created_by),
            modified_by=Utility.return_instance_id(self.modified_by)
        )

        if all_fields:
            json_object.update(dict())

        return json_object
