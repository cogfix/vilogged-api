# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-28 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointments',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]