# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 19:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0004_auto_20171210_1856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alarm',
            name='days',
        ),
        migrations.RemoveField(
            model_name='alarm',
            name='time',
        ),
        migrations.AddField(
            model_name='alarm',
            name='friday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alarm',
            name='monday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alarm',
            name='saturday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alarm',
            name='sunday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alarm',
            name='thursday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alarm',
            name='tuesday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alarm',
            name='wednesday',
            field=models.BooleanField(default=False),
        ),
    ]
