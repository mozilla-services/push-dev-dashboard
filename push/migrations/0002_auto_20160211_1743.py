# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-11 17:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('push', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushapplication',
            name='jws_key',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
