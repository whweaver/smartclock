# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 02:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0009_alarm_sunrise_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alarm',
            name='sunrise_color',
            field=models.FloatField(default=0),
        ),
    ]
