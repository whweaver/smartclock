# Views related to alarms

from django.shortcuts import render
from django.http import JsonResponse
from alarm.forms import AccountForm
from alarm.models import MusicAccount

import sys
import os
sys.path.append(os.path.abspath("../core/app"))

from pandora_service import PandoraService

def accounts(request):
    context = dict()
    context['page'] = 'accounts'
    context['accounts'] = MusicAccount.objects.order_by('id')
    return render(request, 'alarm/accounts.html', context)

def account(request, accountid):
    context = dict()
    context['page'] = 'accounts'
    context['accountid'] = None

    context['form'] = AccountForm()
    if accountid != 'new':
        acct = MusicAccount.objects.get(id=accountid)
        context['accountid'] = acct.id
        context['form'] = AccountForm(instance=acct)
    return render(request, 'alarm/account.html', context)

def change_account(request):
    data = {'valid': False, 'action': 'save'}
    if request.method == 'POST':
        if request.POST['button'] == 'save':
            if 'id' in request.POST:
                account = MusicAccount.objects.get(id=request.POST['id'])
                form = AccountForm(request.POST, instance=account)
            else:
                form = AccountForm(request.POST)
            if form.is_valid():
                if verify_account(form):
                    try:
                        form.save()
                        data['valid'] = True
                    except:
                        pass
        elif request.POST['button'] == 'delete':
            data['action'] = 'delete'
            try:
                MusicAccount.objects.filter(id=int(request.POST['id'])).delete()
                data['valid'] = True
            except:
                pass

    return JsonResponse(data)

def verify_account(form):
    valid = False
    svc = None
    if(form.cleaned_data['service'] == 'P'):
        svc = PandoraService()

    if svc is not None:
        try:
            svc.login(form.cleaned_data['username'], form.cleaned_data['password'])
            valid = True
        except:
            pass
        svc.logout()
    
    return valid
