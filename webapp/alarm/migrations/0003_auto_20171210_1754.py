# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0002_auto_20171105_0321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarm',
            name='name',
        ),
        migrations.AddField(
            model_name='alarm',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]