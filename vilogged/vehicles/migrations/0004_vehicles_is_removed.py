# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-19 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_auto_20160527_2335'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicles',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
