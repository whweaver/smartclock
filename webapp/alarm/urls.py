from django.conf.urls import url

from . import views
from . import views_alarms
from . import views_accounts

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^alarms/enable', views_alarms.enable_alarm, name="enable_alarm"),
    url(r'^alarms', views_alarms.alarms, name="alarms"),
    url(r'^alarm/(?P<alarmid>\d+|new)', views_alarms.alarm, name="alarm"),
    url(r'^alarm/get_playlists', views_alarms.get_alarm_playlists, name="get_alarm_playlists"),
    url(r'^alarm/change', views_alarms.change_alarm, name="change_alarm"),
    url(r'^accounts', views_accounts.accounts, name="accounts"),
    url(r'^account/(?P<accountid>\d+|new)', views_accounts.account, name="account"),
    url(r'^account/change', views_accounts.change_account, name="change_account"),
    url(r'^settings', views.settings, name="settings"),
]
