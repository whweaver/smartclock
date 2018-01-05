# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-05 03:21
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MusicAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(choices=[('P', 'Pandora'), ('G', 'Google Play'), ('S', 'Spotify')], default='P', max_length=1)),
                ('username', models.CharField(default='', max_length=256)),
                ('password', models.CharField(default='', max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='alarm',
            name='music_fade',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AddField(
            model_name='alarm',
            name='music_vol',
            field=models.FloatField(default=0.5),
        ),
        migrations.AddField(
            model_name='alarm',
            name='sunrise_brightness',
            field=models.FloatField(default=1),
        ),
        migrations.AddField(
            model_name='alarm',
            name='sunrise_fade',
            field=models.DurationField(default=datetime.timedelta(0, 1800)),
        ),
        migrations.AlterField(
            model_name='alarm',
            name='days',
            field=models.CharField(blank=True, default='', max_length=27, null=True),
        ),
        migrations.AlterField(
            model_name='alarm',
            name='name',
            field=models.CharField(default='', max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='alarm',
            name='time',
            field=models.TimeField(default=datetime.time(6, 0)),
        ),
        migrations.AddField(
            model_name='alarm',
            name='music_source',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='alarm.MusicAccount'),
        ),
    ]