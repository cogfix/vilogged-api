# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-25 13:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicles',
            old_name='appointment_id',
            new_name='appointment',
        ),
        migrations.RenameField(
            model_name='vehicles',
            old_name='vehicle_type',
            new_name='type',
        ),
    ]
