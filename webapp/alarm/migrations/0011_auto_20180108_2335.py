# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 04:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0010_auto_20180108_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alarm',
            name='sunrise_brightness',
            field=models.FloatField(default=1),
        ),
    ]
