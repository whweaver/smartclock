from django.db import models
import datetime

import sys
import os
sys.path.append(os.path.abspath("../core/lib"))

from pandora_service import PandoraService

class MusicAccount(models.Model):
    SUPPORTED_SERVICE_TYPES = (
        ('P', 'Pandora'),
        ('G', 'Google Play'),
        ('S', 'Spotify'),
    )

    service = models.CharField(blank=False,
                               null=False,
                               max_length=1,
                               choices=SUPPORTED_SERVICE_TYPES,
                               default='P')
    username = models.CharField(blank=False,
                                null=False,
                                max_length=256,
                                default='')
    password = models.CharField(blank=False,
                                null=False,
                                max_length=256,
                                default='')

    def __str__(self):
        names = {
            'P': 'Pandora',
            'S': 'Spotify',
            'G': 'Google Play'
        }
        return '{} ({})'.format(names[self.service], self.username)

    def __eq__(self, other):
        if isinstance(other, MusicAccount):
            return ((self.service == other.service) and
                    (self.username == other.username) and
                    (self.password == other.password))
        else:
            return NotImplemented

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return eq
        else:
            return not eq

    def get_service(self):
        if self.service == 'P':
            svc = PandoraService()

        return svc

    def login(self):
        self.svc = self.get_service()
        self.svc.login(self.username, self.password)

    def logout(self):
        self.svc.logout()

    def get_playlists(self):
        return self.svc.get_playlists()

    def play_playlist(self, playlist_id):
        self.svc.play_playlist(playlist_id)

    def stop_playing(self):
        self.svc.stop_playing()

class Alarm(models.Model):
    enabled = models.BooleanField(blank=False,
                                  null=False,
                                  default=True)
    time = models.TimeField(blank = False,
                            null = False,
                            default=datetime.time(hour=6))
    days = models.CharField(blank=True,
                            null=False,
                            default="",
                            max_length=64)
    music_account = models.ForeignKey(MusicAccount,
                                     blank=True,
                                     null=True,
                                     on_delete=models.SET_NULL,
                                     default=None)
    music_playlist = models.CharField(blank=True,
                                      null=True,
                                      default=None,
                                      max_length=1024)
    music_fade = models.DurationField(blank=False,
                                      null=False,
                                      default=datetime.timedelta(seconds=30))
    music_vol = models.FloatField(blank=False,
                                  null=False,
                                  default=0.5)
    sunrise_fade = models.DurationField(blank=False,
                                        null=False,
                                        default=datetime.timedelta(minutes=30))
    sunrise_brightness = models.FloatField(blank=False,
                                           null=False,
                                           default=1)
    sunrise_color = models.FloatField(blank=False,
                                      null=False,
                                      default=0)

    def get_days_display(self):
        if self.days == 'Mon, Tue, Wed, Thu, Fri, Sat, Sun, ':
            return 'Every Day'
        elif self.days == 'Mon, Tue, Wed, Thu, Fri, ':
            return 'Weekdays'
        elif self.days == 'Sat, Sun, ':
            return 'Weekends'
        elif self.days == '':
            return 'One Time'
        else:
            return self.days[:-2]

    def get_hour(self):
        if self.time.hour > 12:
            hour = self.time.hour - 12
        elif self.time.hour == 0:
            hour = 12
        else:
            hour = self.time.hour
        return hour

    def get_time_display(self):
        minute = '{0:{fill}2}'.format(self.time.minute, fill='0')
        return '{}:{}'.format(str(self.get_hour()), minute)

    def get_ampm_display(self):
        if self.time.hour >= 12:
            ampm = 'pm'
        else:
            ampm = 'am'
        return ampm

    def get_sunrise_fade_display(self):
        return round(self.sunrise_fade.total_seconds() / 60)

    def get_playlist_display(self):
        display = ''
        if self.music_account is not None:
            self.music_account.login()
            playlists = self.music_account.get_playlists()
            self.music_account.logout()
            for token, name in playlists.items():
                if token == self.music_playlist:
                    display = name

        return display
