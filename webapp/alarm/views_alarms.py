# Views related to alarms
import operator

from django.shortcuts import render
from django.http import JsonResponse
from alarm.forms import AlarmForm, AlarmPlaylistsForm
from alarm.models import Alarm, MusicAccount

import sys
import os
sys.path.append(os.path.abspath("../core/app"))

from pandora_service import PandoraService

def alarms(request):
    context = dict()
    context['page'] = 'alarms'
    context['alarms'] = Alarm.objects.order_by('id')
    return render(request, 'alarm/alarms.html', context)

def enable_alarm(request):
    data = {'valid': False}
    if request.method == 'POST':
        if 'alarmid' in request.POST:
            try:
                data['alarmid'] = request.POST['alarmid']
                alrm = Alarm.objects.get(id=request.POST['alarmid'])
                alrm.enabled = not alrm.enabled
                alrm.save()
                data['valid'] = True
                data['enabled'] = alrm.enabled
            except:
                pass

    return JsonResponse(data)

def alarm(request, alarmid):
    context = dict()
    context['page'] = 'alarms'
    
    if alarmid == 'new':
        context['alarmid'] = None
        context['form'] = AlarmForm()
    else:
        alrm = Alarm.objects.get(id=alarmid)
        context['alarmid'] = alarmid
        context['form'] = AlarmForm(instance=alrm)

    return render(request, 'alarm/alarm.html', context)

def get_alarm_playlists(request):
    context = dict()
    if request.method == 'POST':
        form = AlarmPlaylistsForm(request.POST)
        if form.is_valid():
            try:
                acct = form.cleaned_data['music_account']
                acct.login()
                unsorted_playlists = acct.get_playlists()
                acct.logout()
                context['playlists'] = sorted(unsorted_playlists.items(), key=operator.itemgetter(1))
            except:
                pass

    return render(request, 'alarm/playlists.html', context)

def change_alarm(request):
    data = {'valid': False, 'action': 'save'}
    if request.method == 'POST':
        if request.POST['button'] == 'save':
            if 'id' in request.POST:
                alrm = Alarm.objects.get(id=request.POST['id'])
                form = AlarmForm(request.POST, instance=alrm)
            else:
                form = AlarmForm(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    data['valid'] = True
                except:
                    pass
            else:
                print(form.errors)
        elif request.POST['button'] == 'delete':
            data['action'] = 'delete'
            try:
                Alarm.objects.filter(id=int(request.POST['id'])).delete()
                data['valid'] = True
            except:
                pass

    return JsonResponse(data)
