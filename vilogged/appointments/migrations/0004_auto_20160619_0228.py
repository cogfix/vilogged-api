# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-19 01:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0003_auto_20160529_2340'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointments',
            old_name='is_deleted',
            new_name='is_removed',
        ),
    ]