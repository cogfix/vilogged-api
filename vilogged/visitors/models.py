from django.db import models
from vilogged.users.models import UserProfile
from vilogged.company.models import Company
from utility.utility import Utility
from datetime import date, datetime

class VisitorTypes(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    black_listed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'visitors'

    def __unicode__(self):
        return '{0}'.format(self.name)

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            name=self.name,
            black_listed=self.black_listed,
            created=Utility.format_datetime(self.created),
            modified=Utility.format_datetime(self.modified),
            created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
            modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object


class VisitorGroup(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    appointment = models.CharField(max_length=100, blank=True, null=True)
    visitors = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    modified_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        app_label = 'visitors'

    def __unicode__(self):
        return '{0}'.format(self.name)

    def to_json(self, all_fields=False):

        json_object = dict(
                _id=self._id,
                _rev=self._rev,
                appointment=self.appointment,
                visitors=self.visitors,
                created=Utility.format_datetime(self.created),
                modified=Utility.format_datetime(self.modified),
                created_by=Utility.get_instance_fields(self.created_by, ['_id', 'username']),
                modified_by=Utility.get_instance_fields(self.modified_by, ['_id', 'username'])
        )

        if all_fields:
            json_object.update(dict())

        return json_object


class Visitors(models.Model):
    _id = models.CharField(max_length=100, unique=True, primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=7, default='Male', null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, verbose_name='visitors phone number')
    black_listed = models.BooleanField(default=False)
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
    type = models.ForeignKey(VisitorTypes, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='created_by')
    modified_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name='modified_by')

    class Meta:
        app_label = 'visitors'

    def __unicode__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            gender=self.gender,
            phone=self.phone,
            black_listed=self.black_listed,
            occupation=self.occupation,
            company=self.get_company(),
            date_of_birth=Utility.format_datetime(self.date_of_birth),
            nationality=self.nationality,
            state_of_origin=self.state_of_origin,
            lga_of_origin=self.lga_of_origin,
            pass_code=self.pass_code,
            type=self.get_type(),
            created=Utility.format_datetime(self.created),
            modified=Utility.format_datetime(self.modified),
            created_by=Utility.return_instance_id(self.created_by),
            modified_by=Utility.return_instance_id(self.modified_by)
        )

        if all_fields:
            json_object.update(dict(
                image=self.image,
                fingerprint=self.fingerprint,
                signature=self.signature,
            ))

        return json_object

    def get_type(self):

        if self.type is not None:
            return self.type.to_json()
        return self.type

    def get_company(self):

        if self.company is not None:
            return self.company.to_json()
        return self.company

