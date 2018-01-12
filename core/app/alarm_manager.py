# Provides functionality for processing the alarms

import threading
import datetime

import pi_io
import alarm.models

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SNOOZE_TIME = datetime.timedelta(minutes=10)

def get_days_from_day(day):
    day_idx = WEEKDAYS.index(day)
    return WEEKDAYS[day_idx:] + WEEKDAYS[:day_idx]

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
        for alarmid, alarm in self.alarms.items():
            alarm.snooze()

    def reset(self):
        for alarmid, alarm in self.alarms.items():
            alarm.reset()

    def process(self):
        self.snooze_button.process()
        for alarmid, alarm in self.alarms.items():
            alarm.process()

class Alarm:
    def __init__(self, db_alarm, manager):
        self.manager = manager
        self.db_alarm = db_alarm
        alarm_time = self.get_next_alarm_time(True)
        self.sunrise = AlarmSunrise(alarm_time, db_alarm.sunrise_fade, db_alarm.sunrise_brightness, db_alarm.sunrise_color)
        self.music = AlarmMusic(alarm_time, db_alarm.music_fade, db_alarm.music_account, db_alarm.music_playlist, db_alarm.music_vol)

    def get_next_alarm_time(self, ignore_days=False):
        next_date = self.get_next_alarm_date(ignore_days)
        if next_date is None:
            time = None
        else:
            time = datetime.datetime.combine(next_date, self.db_alarm.time)
        return time

    def get_next_alarm_date(self, ignore_days=False):
        ONE_DAY = datetime.timedelta(days=1)
        if len(self.db_alarm.days) > 0 or ignore_days:
            cur_time = datetime.datetime.now()
            if self.db_alarm.time > cur_time.time():
                weekday_idx = cur_time.weekday()
                next_day = cur_time.date()
            else:
                weekday_idx = cur_time.weekday() + 1
                next_day = cur_time.date() + ONE_DAY

            if len(self.db_alarm.days) > 0:
                upcoming_week = get_days_from_day(WEEKDAYS[weekday_idx])
                for day in upcoming_week:
                    if day in self.db_alarm.days:
                        break
                    next_day += ONE_DAY
        else:
            next_day = None

        return next_day

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

class AlarmComponent:
    def __init__(self, alarm_time, duration):
        self.alarm_time = alarm_time
        self.alarming = False
        self._set_times(alarm_time, duration)

    def _set_times(self, alarm_time, duration):
        self.fade_end_time = alarm_time
        self.fade_duration = duration
        self.nominal_fade_duration = self.fade_duration
        self.fade_start_time = self.fade_end_time - self.fade_duration

    def snooze(self, snooze_time):
        if self.alarming:
            if snooze_time > self.fade_duration:
                duration = self.fade_duration
            else:
                duration = snooze_time
            self._set_times(datetime.datetime.now() + snooze_time, duration)

    def reset(self, new_alarm_time):
        if self.alarming:
            self.alarming = not self._clear_effects()
        if new_alarm_time is not None:
            self._set_times(new_alarm_time, self.fade_duration)

    def process(self):
        cur_time = datetime.datetime.now()
        if cur_time >= self.fade_start_time:
            self.alarming = True
            self._do_effects(cur_time)
        elif self.alarming:
            self._clear_effects()
            self.alarming = False

    def _do_effects(self, cur_time):
        pass

    def _clear_effects(self):
        pass

class AlarmSunrise(AlarmComponent):
    def __init__(self, alarm_time, duration, brightness, color):
        self.io = pi_io.Sunrise()
        self.brightness = brightness
        self.color = color
        self.cur_warm_brightness = 0
        self.cur_cool_brightness = 0
        super().__init__(alarm_time, duration)

    def _do_effects(self, cur_time):
        if cur_time >= self.fade_end_time:
            fade_fraction = 1
        else:
            fade_fraction = (cur_time - self.fade_start_time) / self.fade_duration

        if self.color < 0:
            warm_target_fraction = 1
            cool_target_fraction = 1 + self.color
        else:
            warm_target_fraction = 1 - self.color
            cool_target_fraction = 1

        if fade_fraction < 0.5:
            warm_fade_fraction = warm_target_fraction * fade_fraction * 2
            cool_fade_fraction = 0
        else:
            warm_fade_fraction = warm_target_fraction
            cool_fade_fraction = cool_target_fraction * (fade_fraction - 0.5) * 2

        warm_brightness = warm_fade_fraction * self.brightness
        cool_brightness = cool_fade_fraction * self.brightness

        if warm_brightness != self.cur_warm_brightness:
            self.io.set_warm_brightness(warm_brightness)
            self.cur_warm_brightness = warm_brightness

        if cool_brightness != self.cur_cool_brightness:
            self.io.set_cool_brightness(cool_brightness)
            self.cur_cool_brightness = cool_brightness

    def _clear_effects(self):
        self.io.set_warm_brightness(0)
        self.io.set_cool_brightness(0)

class AlarmMusic(AlarmComponent):
    def __init__(self, alarm_time, duration, account, playlist, volume):
        self.speaker = pi_io.Speaker()
        self.account = account
        self.playlist = playlist
        self.volume = volume
        self.music_playing = False
        self.cur_volume = 0
        super().__init__(alarm_time, duration)

    def _do_effects(self, cur_time):
        if cur_time >= self.fade_end_time:
            fade_fraction = 1
        else:
            fade_fraction = (cur_time - self.fade_start_time) / self.fade_duration

        volume = fade_fraction * self.volume

        if volume != self.cur_volume:
            self.speaker.set_volume(volume)
            self.cur_volume = volume

        if not self.music_playing:
            try:
                self.account.login()
                self.account.play_playlist(self.playlist)
                self.music_playing = True
            except:
                print("Failed to play playlist")
                try:
                    self.account.stop_playing()
                    self.account.logout()
                    self.music_playing = False
                except:
                    self._clear_effects()

    def _clear_effects(self):
        if self.music_playing:
            try:
                self.account.stop_playing()
                self.account.logout()
                self.music_playing = False
            except:
                print("Failed to stop music")
