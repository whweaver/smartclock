from alarm import models
from django import forms

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
                  'sunrise_brightness']
        widgets = {
            'music_playlist': forms.Select(),
            'music_vol': RangeInput(
                            attrs = {
                                'min': 0,
                                'max': 1,
                                'value': 0.5,
                                'step_size': 0.01
                            }
                          ),
            'sunrise_brightness': RangeInput(
                            attrs = {
                                'min': 0,
                                'max': 1,
                                'value': 0.5,
                                'step_size': 0.01
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

    AMPM_CHOICES = (('AM', 'AM'), ('PM', 'PM'))
    ampm = forms.ChoiceField(choices=AMPM_CHOICES)

    for day_attr, day_abrev in DAYS:
        vars()[day_attr] = forms.BooleanField()

    music_fade_seconds = forms.IntegerField(widget=RangeInput(attrs = {'min': 0, 'max': 90, 'value': 30, 'step_size': 1}))
    sunrise_fade_minutes = forms.IntegerField(widget=RangeInput(attrs = {'min': 0, 'max': 90, 'value': 30, 'step_size': 1}))

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            kwargs['initial'] = {
                'hour': kwargs['instance'].get_hour(),
                'minute': kwargs['instance'].time.minute,
                'ampm': 'AM' if kwargs['instance'].time.hour < 12 else 'PM',
                'sunrise_fade_minutes': kwargs['instance'].sunrise_fade.total_seconds() / 60,
                'music_fade_seconds': kwargs['instance'].sunrise_fade.total_seconds()
            }
            for day_attr, day_abrev in AlarmForm.DAYS:
                if day_abrev in kwargs['instance'].days:
                    kwargs['initial'][day_attr] = True
                else:
                    kwargs['initial'][day_attr] = False

        super().__init__(*args, **kwargs)

        if 'instance' in kwargs:
            try:
                acct = kwargs['instance'].music_account
                acct.login()
                playlists = tuple(acct.get_playlists().items())
                acct.logout()
                self.fields['music_playlist'].choices = playlists
                self.fields['music_playlist'].widget.choices = playlists
            except:
                pass

    def save(self, commit=True):
        if self.cleaned_data['ampm'] == 'PM':
            hour = self.cleaned_data['hour'] + 12
        elif self.cleaned_data['hour'] == 12:
            hour = 0
        else:
            hour = self.cleaned_data['hour']
        self.instance.time = datetime.time(hour=hour, minute=self.cleaned_data['minute'])

        days = ''
        for day_attr, day_abrev in DAYS:
            if self.cleaned_data[day_attr]:
                days += day_abrev + ', '
        self.instance.days = days

        self.instance.sunrise_fade = datetime.timedelta(minutes=self.cleaned_data['sunrise_fade_minutes'])
        self.instance.music_fade = datetime.timedelta(seconds=self.cleaned_data['sunrise_fade_seconds'])

        if commit == True:
            self.instance.save()

        return self.instance

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
