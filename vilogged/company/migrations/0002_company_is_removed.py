# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-19 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]
