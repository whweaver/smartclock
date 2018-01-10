import math
import datetime
import operator

from django import forms

from alarm import models

class RangeInput(forms.NumberInput):
    input_type = 'range'

class AccountChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        image_tags = {
            'P': '<img src="/static/shared/images/pandora.png" class="alarm-account-image" />',
            'S': '<img src="/static/shared/images/spotify.png" class="alarm-account-image" />',
            'G': '<img src="/static/shared/images/google_play.png" class="alarm-account-image" />'
        }
        return '{} {}'.format(image_tags[obj.service], obj.username)

class AlarmForm(forms.ModelForm):
    DAYS = (
            ('monday', 'Mon'),
            ('tuesday', 'Tue'),
            ('wednesday', 'Wed'),
            ('thursday', 'Thu'),
            ('friday', 'Fri'),
            ('saturday', 'Sat'),
            ('sunday', 'Sun')
        )

    class Meta:
        model = models.Alarm
        fields = ['enabled',
                  'music_account', 'music_playlist', 'music_vol',
                  'sunrise_brightness', 'sunrise_color']
        widgets = {
            'music_playlist': forms.Select(),
            'music_vol': RangeInput(
                            attrs = {
                                'min': 0,
                                'max': 1,
                                'value': 0.5,
                                'step_size': 0.01,
                                'class': 'slider'
                            }
                          ),
            'sunrise_brightness': RangeInput(
                            attrs = {
                                'min': 0,
                                'max': 1,
                                'value': 0.5,
                                'step_size': 0.01,
                                'class': 'slider'
                            }
                          ),
            'sunrise_color': RangeInput(
                            attrs = {
                                'min': -1,
                                'max': 1,
                                'value': 0,
                                'step_size': 0.01,
                                'class': 'slider'
                            }
                          )
        }

    hours_list = [(12, '12')]
    for i in range(1, 12):
        hours_list.append((i, str(i)))
    HOURS = tuple(hours_list)
    hour = forms.ChoiceField(choices=HOURS, widget=forms.Select(attrs = {'dir': 'rtl'}))

    minutes_list = []
    for i in range(60):
        minutes_list.append((i, '{0:{fill}2}'.format(i, fill='0')))
    MINUTES = tuple(minutes_list)
    minute = forms.ChoiceField(choices=MINUTES)

    AMPM_CHOICES = (('am', 'am'), ('pm', 'pm'))
    ampm = forms.ChoiceField(widget=forms.HiddenInput, choices=AMPM_CHOICES)

    for day_attr, day_abrev in DAYS:
        vars()[day_attr] = forms.BooleanField(widget=forms.HiddenInput, required=False)

    music_fade_seconds = forms.IntegerField(widget=RangeInput(attrs = {'min': 0, 'max': 90, 'value': 30, 'step_size': 1, 'class': 'slider'}))
    sunrise_fade_minutes = forms.IntegerField(widget=RangeInput(attrs = {'min': 0, 'max': 90, 'value': 30, 'step_size': 1, 'class': 'slider'}))

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs['initial'] = {
                'hour': kwargs['instance'].get_hour(),
                'minute': kwargs['instance'].time.minute,
                'ampm': 'am' if kwargs['instance'].time.hour < 12 else 'pm',
                'sunrise_fade_minutes': kwargs['instance'].sunrise_fade.total_seconds() / 60,
                'music_fade_seconds': kwargs['instance'].music_fade.total_seconds()
            }
            for day_attr, day_abrev in AlarmForm.DAYS:
                if day_abrev in kwargs['instance'].days:
                    kwargs['initial'][day_attr] = True
                else:
                    kwargs['initial'][day_attr] = False
        else:
            kwargs['initial'] = {
                'hour': 6,
                'minute': 0,
                'ampm': 'am',
                'sunrise_fade_minutes': 30,
                'music_fade_seconds': 30
            }
            for day_attr, day_abrev in AlarmForm.DAYS:
                kwargs['initial'][day_attr] = False

        super().__init__(*args, **kwargs)

        if 'instance' in kwargs:
            try:
                acct = kwargs['instance'].music_account
                acct.login()
                unsorted_playlists = acct.get_playlists()
                acct.logout()
                playlists = sorted(unsorted_playlists.items(), key=operator.itemgetter(1))
                self.fields['music_playlist'].choices = playlists
                self.fields['music_playlist'].widget.choices = playlists
            except:
                pass

    def save(self, commit=True):
        hour_num = int(self.cleaned_data['hour'])
        min_num = int(self.cleaned_data['minute'])
        if self.cleaned_data['ampm'] == 'PM':
            hour = hour_num + 12
        elif hour_num == 12:
            hour = 0
        else:
            hour = hour_num
        self.instance.time = datetime.time(hour=hour, minute=min_num)

        days = ''
        for day_attr, day_abrev in AlarmForm.DAYS:
            if self.cleaned_data[day_attr]:
                days += day_abrev + ', '
        self.instance.days = days

        self.instance.sunrise_fade = datetime.timedelta(minutes=self.cleaned_data['sunrise_fade_minutes'])
        self.instance.music_fade = datetime.timedelta(seconds=self.cleaned_data['music_fade_seconds'])

        self.instance.enabled = True

        if commit == True:
            self.instance.save()

        return self.instance

    def music_vol_display(self):
        val = round(self.instance.music_vol * 100)
        if val > 100:
            val = 100
        return val

    def music_fade_display(self):
        val = round(self.instance.music_fade.total_seconds())
        if val > 99:
            val = '??'
        return val

    def sunrise_brightness_display(self):
        raw = self.instance.sunrise_brightness
        if raw > 1:
            raw = 1
        color_adj = (1 - abs(self.instance.sunrise_color)) * 0.5 + 0.5
        val = round(raw * color_adj * 100)
        return val

    def sunrise_fade_display(self):
        val = round(self.instance.sunrise_fade.total_seconds() / 60)
        if val > 99:
            val = '??'
        return val

    def sunrise_color_rgb(self):
        temp = range_to_temp(self.instance.sunrise_color)
        rgb = temp_to_rgb(temp)
        return rgb

def range_to_temp(rng):
    neg_range = -rng
    WARM = 2200
    COOL = 5700

    warm_weight = 1
    cool_weight = 1

    if neg_range < 0:
        warm_weight = 1
        cool_weight = 1 + neg_range
    else:
        warm_weight = 1 - neg_range
        cool_weight = 1

    temp = (WARM * warm_weight + COOL * cool_weight) / (warm_weight + cool_weight)
    return temp

def temp_to_rgb(temp):
    red = 255
    green = 255
    blue = 255
    adj_temp = temp / 100

    if adj_temp <= 66:
        red = 255
    else:
        red = limit_rgb(329.698727446 * pow(adj_temp - 60, -0.1332047592))

    if adj_temp <= 66:
        green = limit_rgb(99.4708025861 * math.log(adj_temp) - 161.1195681661)

    if adj_temp >= 66:
        blue = 255
    else:
        if adj_temp <= 19:
            blue = 0
        else:
            blue = limit_rgb(138.5177312231 * math.log(adj_temp - 10) - 305.0447927307)

    rgb = "{:02X}{:02X}{:02X}".format(int(red), int(green), int(blue))
    return rgb

def limit_rgb(value):
    if value < 0:
        limited_value = 0
    elif value > 255:
        limited_value = 255
    else:
        limited_value = value
    return limited_value

class AlarmPlaylistsForm(forms.ModelForm):
    class Meta:
        model = models.Alarm
        fields = ['music_account']

class AccountForm(forms.ModelForm):
    class Meta:
        model = models.MusicAccount
        fields = ['service', 'username', 'password']
        widgets = {
            'service': forms.Select(
                        attrs = {
                            'class': 'account-form-input-service'
                        }
                       ),
            'username': forms.TextInput(
                            attrs = {
                                'class': 'account-form-input-username',
                                'placeholder': 'username'
                            }
                        ),
            'password': forms.PasswordInput(
                            attrs = {
                                'class': 'account-form-input-password',
                                'placeholder': 'password'
                            }
                        )
        }
