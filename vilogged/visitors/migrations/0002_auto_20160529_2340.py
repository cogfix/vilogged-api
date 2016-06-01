# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-29 22:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitors', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visitorgroup',
            old_name='params',
            new_name='visitors',
        ),
        migrations.RemoveField(
            model_name='visitorgroup',
            name='black_listed',
        ),
        migrations.RemoveField(
            model_name='visitorgroup',
            name='name',
        ),
        migrations.RemoveField(
            model_name='visitors',
            name='group',
        ),
        migrations.AddField(
            model_name='visitorgroup',
            name='appointment',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='visitors',
            name='black_listed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='visitors',
            name='gender',
            field=models.CharField(blank=True, default=b'Male', max_length=7, null=True),
        ),
    ]