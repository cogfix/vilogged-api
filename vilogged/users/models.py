from django.db import models
from vilogged.department.models import Department
from django.contrib.auth.models import AbstractUser
from utility.utility import Utility


class UserProfile(AbstractUser, models.Model):
    _id = models.CharField(max_length=100,  unique=True,  primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    gender = models.CharField(max_length=100, default='Male')
    phone = models.CharField(max_length=100, unique=True)
    home_phone = models.CharField(max_length=100, blank=True, null=True)
    work_phone = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    is_removed = models.BooleanField(default=False)

    class Meta:
        app_label = 'users'

    def __unicode__(self):
        return '{}'.format(self.username)

    @classmethod
    def model_fields(cls):
        return ['first_name', 'last_name', 'description']

    def get_department(self):
        return self.department

    def get_department_or_object(self, all_fields):
        department = dict()
        if self.department:
            department = self.department.to_json(all_fields)
        return department

    def to_json(self, all_fields=False):

        json_object = dict(
            _id=self._id,
            _rev=self._rev,
            email=self.email,
            last_name=self.last_name,
            first_name=self.first_name,
            username=self.username,
            is_superuser=self.is_superuser,
            is_active=self.is_active,
            is_staff=self.is_staff,
            date_joined=Utility.format_datetime(self.date_joined),
            last_login=Utility.format_datetime(self.last_login),
            groups=list(self.get_group_permissions(self.groups)),
            user_permissions=list(self.get_all_permissions(self.user_permissions)),
            phone=self.phone,
            work_phone=self.work_phone,
            gender=self.gender,
            home_phone=self.home_phone,
            department=self.get_department_or_object(all_fields),
        )

        if all_fields:
            json_object.update(dict(
                password=self.password,
                image=self.image
            ))

        return json_object
