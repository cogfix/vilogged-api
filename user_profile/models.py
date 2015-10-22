__author__ = 'musa'
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models


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

    class Meta:
        app_label = 'core'

    def __unicode__(self):
        return '{}'.format(self.name)


class UserProfile(AbstractUser, models.Model):
    _id = models.CharField(max_length=100,  unique=True,  primary_key=True)
    _rev = models.CharField(max_length=100,  unique=True, editable=False)
    gender = models.CharField(max_length=10, default='Male')
    phone = models.CharField(max_length=20, unique=True)
    home_phone = models.CharField(max_length=20, blank=True, null=True)
    work_phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.ForeignKey(Department, null=True, blank=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'user_profile'

    def __unicode__(self):
        return '{}'.format(self.username)

    def clean(self):
        if self.first_name is None:
            raise ValidationError(_('Draft entries may not have a publication date.'))

