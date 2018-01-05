# Generic views

from django.shortcuts import render

from . import views_alarms

def index(request):
    return views_alarms.alarms(request)

def settings(request):
    context = dict()
    context['page'] = 'settings'
    return render(request, 'alarm/settings.html', context)
