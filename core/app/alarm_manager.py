# Provides functionality for processing the alarms

import threading
import datetime

import pi_io
import alarm.models

class AlarmManager:
    def __init__(self):
        self.snooze_button = pi_io.SnoozeButton(self)
        self.alarms = {}
        for db_alarm in alarm.models.Alarm.objects.filter(enabled__exact=True):
            self.alarms[db_alarm.id] = Alarm(db_alarm, self)

    def refresh(self):
        for db_alarm in alarm.models.Alarm.objects.filter(enabled__exact=True):
            if db_alarm.id in self.alarms:
                self.alarms[db_alarm.id].refresh(db_alarm)
            else:
                self.alarms[db_alarm.id] = Alarm(db_alarm, self)

    def snooze(self):
        for alarm in self.alarms:
            alarm.snooze()

    def reset(self):
        for alarm in self.alarms:
            alarms.reset()

    def process(self):
        self.snooze_button.process()
        for alarm in self.alarms:
            alarm.process()

class Alarm:
    WEEKDAYS = ["Mon, Tue, Wed, Thu, Fri, Sat, Sun"]
    SNOOZE_TIME = datetime.timedelta(minutes=10)

    def __init__(self, db_alarm, manager):
        self.manager = manager
        self.db_alarm = db_alarm
        alarm_time = self.get_next_alarm_time()
        self.sunrise = AlarmSunrise(db_alarm.sunrise_brightness, ddb_alarm.sunrise_fade, alarm_time)
        self.music = AlarmMusic(db_alarm.music_account, db_alarm.playlist, db_alarm.volume, db_alarm.music_fade, alarm_time)

    def get_next_alarm_time(self):
        next_date = self.get_next_alarm_date()
        if next_date is None:
            time = None
        else:
            time = datetime.datetime.combine(next_date, self.db_alarm.time)
        return time

    def get_next_alarm_date(self):
        if len(self.db_alarm.days) > 0:
            ONE_DAY = datetime.timedelta(days=1)
            cur_time = datetime.datetime.now()
            if self.alarm_time > cur_time.time():
                weekday_idx = cur_time.weekday()
                next_day = cur_time.date()
            else:
                weekday_idx = cur_time.weekday() + 1
                next_day = cur_time.date() + ONE_DAY
            upcoming_week = get_days_from_day(WEEKDAYS[weekday_idx])
            for day in upcoming_week:
                if day in db_alarms.days:
                    break
                next_day += ONE_DAY
        else:
            next_day = None

        return next_day

    def get_days_from_day(day):
        day_idx = WEEKDAYS.index(day)
        return WEEKDAYS[day_idx:] + DAYS[:day_idx]

    def refresh(self, db_alarm):
        self.reset()
        self.db_alarm = db_alarm
        alarm_time = self.get_next_alarm_time()
        self.sunrise = AlarmSunrise(db_alarm.sunrise_brightness, db_alarm.sunrise_fade, alarm_time)
        self.music = AlarmMusic(db_alarm.music_account, db_alarm.playlist, db_alarm.volume, db_alarm.music_fade, alarm_time)

    def snooze(self):
        if self.sunrise is not None:
            self.sunrise.snooze(SNOOZE_TIME)
        if self.music is not None:
            self.music.snooze(SNOOZE_TIME)

    def reset(self):
        alarm_time = self.get_next_alarm_time()
        self.sunrise.reset(alarm_time)
        self.music.reset(alarm_time)
        if alarm_time is None:
            self.sunrise = None
            self.music = None
            db_alarm.enabled = False
            db_alarm.save()
            self.manager.refresh()

    def process(self):
        if self.sunrise is not None:
            self.sunrise.process()
        if self.music is not None:
            self.music.process()

class AlarmSunrise:
    def __init__(self, brightness, fade_time, alarm_time):
        self.io = pi_io.Sunrise()
        self.brightness = brightness
        self.set_times(alarm_time)

    def set_times(self, alarm_time):
        self.fade_end_time = alarm_time
        self.fade_duration = fade_time
        self.nominal_fade_duration = self.fade_duration
        self.fade_start_time = self.fade_end_time - self.fade_duration

    def snooze(self, snooze_time):
        self.fade_end_time = datetime.datetime.now() + snooze_time
        if snooze_time < self.fade_duration:
            self.fade_duration = snooze_time
        self.fade_start_time = self.fade_end_time - self.fade_duration

    def reset(self, alarm_time):
        self.io.set_warm_brightness(0)
        self.io.set_cool_brightness(0)
        if alarm_time is not None:
            self.set_times(alarm_time)

    def process(self):
        cur_time = datetime.datetime.now()
        if cur_time >= self.fade_start_time:
            if cur_time >= self.fade_end_time:
                fade_fraction = 1
            else:
                fade_fraction = (cur_time - self.fade_start_time) / self.fade_duration

            if fade_fraction < 0.5:
                warm_fade_fraction = fade_fraction * 2
                cool_fade_fraction = 0
            else:
                warm_fade_fraction = 1
                cool_fade_fraction = (fade_fraction - 0.5) * 2

            warm_brightness = warm_fade_fraction * self.brightness
            cool_brightnesss = cool_fade_fraction * self.brightness

            self.io.set_warm_brightness(warm_brightness)
            self.io.set_cool_brightness(cool_brightness)

class AlarmMusic:
    def __init__(self, account, playlist, volume, fade_time, alarm_time):
        self.speaker = pi_io.Speaker()
        self.account = account
        self.playlist = playlist
        self.volume = db_alarm.music_volume
        self.music_playing = False
        self.set_times()

    def set_times(self, alarm_time):
        self.fade_start_time = alarm_time
        self.fade_duration = fade_time
        self.fade_end_time = self.fade_start_time + self.fade_duration

    def snooze(self, snooze_time):
        self.set_times(datetime.datetime.now() + snooze_time)

    def reset(self, alarm_time):
        self.speaker.set_volume(0)
        try:
            self.account.stop_playing()
            self.account.logout()
            self.music_playing = False
        except:
            pass
        if alarm_time is not None:
            self.set_times(alarm_time)

    def process(self):
        cur_time = datetime.datetime.now()
        if cur_time >= self.fade_start_time:
            if cur_time >= self.fade_end_time:
                fade_fraction = 1
            else:
                fade_fraction = (cur_time - self.fade_start_time) / self.fade_duration

            volume = fade_fraction * self.volume

            self.speaker.set_volume(volume)

            if not self.music_playing:
                try:
                    self.account.login()
                    self.account.play_playlist(self.playlist)
                    self.music_playing = True
                except:
                    pass

        elif self.music_playing:
            try:
                self.account.stop_playing()
                self.account.logout()
                self.music_playing = False
            except:
                pass
