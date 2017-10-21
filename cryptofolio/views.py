# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Max, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext

from . import forms
from . import models

from api.Coinmarketcap import Coinmarket

@login_required
def home(request):
    exchange_accounts = models.ExchangeAccount.objects.filter(user=request.user)

    if not exchange_accounts:
        return render(request, 'home.html', {'has_data': False})

    fiat = request.user.userprofile.fiat

    # get current rates
    market = Coinmarket()
    rates = market.getRates(fiat)
    balances = []
    crypto_balances = {}

    history_data = {}
    currencies = []

    for exchange_account in exchange_accounts:
        exchange_balances = models.ExchangeBalance.objects.filter(
            exchangeAccount=exchange_account
        )
        latest_exchange_balances = get_latest_exchange_balances(
            exchange_balances
        )

        # aggregate latest balances
        for exchange_balance in latest_exchange_balances:
            currency = exchange_balance.currency
            amount = exchange_balance.amount

            if currency in crypto_balances:
                crypto_balances[currency] += amount
            else:
                crypto_balances[currency] = amount

    # convert balances to FIAT
    for currency in crypto_balances:
        if currency in rates:
            balances.append(
                {
                    'currency': currency,
                    'amount': crypto_balances[currency],
                    'amount_fiat': crypto_balances[currency] * rates[currency],
                }
            )

    xdata = [ x['currency'] for x in balances ]
    crypto_ydata = [ x['amount'] for x in balances ]
    fiat_ydata = [ x['amount_fiat'] for x in balances ]

    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " coins"},
    }
    chartdata = {'x': xdata, 'y1': crypto_ydata, 'extra1': extra_serie}
    charttype = "pieChart"
    chartcontainer = 'crypto_container'
    crypto_piechart = {
    	'charttype': charttype,
	'chartdata': chartdata,
	'chartcontainer': chartcontainer,
	'extra': {
	    'x_is_date': False,
	    'x_axis_format': '',
	    'tag_script_js': True,
	    'jquery_on_ready': False,
	    }
	}

    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " "+fiat},
    }
    chartdata = {'x': xdata, 'y1': fiat_ydata, 'extra1': extra_serie}
    charttype = "pieChart"
    chartcontainer = 'fiat_container'
    fiat_piechart = {
    	'charttype': charttype,
	'chartdata': chartdata,
	'chartcontainer': chartcontainer,
	'extra': {
	    'x_is_date': False,
	    'x_axis_format': '',
	    'tag_script_js': True,
	    'jquery_on_ready': False,
	    }
	}

    return render(
        request,
        'home.html',
        {
            'fiat': fiat,
            'balances': balances,
            'fiat_sum': sum(fiat_ydata),
            'has_data': True,
            'crypto_piechart': crypto_piechart,
            'fiat_piechart': fiat_piechart,
        }
    )

@login_required
def settings(request):
    exchanges = models.Exchange.objects.all()
    return render(request, 'settings.html', {'exchanges': exchanges})

@login_required
def exchange(request, exchange_id):
    exchange = get_object_or_404(models.Exchange, pk=exchange_id)
    latest_exchange_balances = None

    if request.method == 'POST':
        form = forms.ExchangeAccountForm(request.POST)
        if form.is_valid():
            exchange_account, created = models.ExchangeAccount.objects.get_or_create(
                user = request.user,
                exchange = exchange
            )
            exchange_account.key = form.cleaned_data.get('key')
            exchange_account.secret = form.cleaned_data.get('secret')

            exchange_account.save()
            has_errors, errors = models.update_exchange_balances([exchange_account])

            if has_errors:
                for error in errors:
                    messages.warning(request, error)
            else:
                messages.success(request, 'Exchange updated successfully!')

            return redirect('exchange', exchange_id=exchange)
        else:
            messages.warning(request, 'There was an error adding exchange!')
    else:
        try:
            exchange_account = models.ExchangeAccount.objects.get(
                user=request.user,
                exchange=exchange
            )
            exchange_balances = models.ExchangeBalance.objects.filter(
                exchangeAccount=exchange_account
            )

            latest_exchange_balances = get_latest_exchange_balances(
                exchange_balances
            )

            form = forms.ExchangeAccountForm(instance=exchange_account)
        except ObjectDoesNotExist:
            form = forms.ExchangeAccountForm()

    return render(
        request,
        'exchange.html',
        {
            'form': form,
            'exchange': exchange,
            'balances': latest_exchange_balances
        }
    )

def signup(request):
    if request.user.is_authenticated:
	return redirect('/')

    if request.method == 'POST':
	form = forms.SignUpForm(request.POST)
	if form.is_valid():
	    form.save()
	    username = form.cleaned_data.get('username')
	    raw_password = form.cleaned_data.get('password1')
	    user = authenticate(username=username, password=raw_password)
	    login(request, user)
	    return redirect('home')
    else:
	form = forms.SignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
@transaction.atomic
def changeDetails(request):
    if request.method == 'POST':
        form = forms.UserChangeDetailsForm(request.POST, instance=request.user)
        fiat_form = forms.UserChangeFiatForm(
            request.POST,
            instance=request.user.userprofile
        )
        if form.is_valid() and fiat_form.is_valid():
            form.save()
            fiat_form.save()
            messages.success(request, 'Your details were successfully updated!')
            return redirect('settings')
        else:
            messages.warning(request, 'There was an error changing your details!')
    else:
        form = forms.UserChangeDetailsForm(instance=request.user)
        fiat_form = forms.UserChangeFiatForm(
            instance=request.user.userprofile
        )

    return render(
        request,
        'change_details.html',
        {
            'form': form,
            'fiat_form': fiat_form
        }
    )

@login_required
def changePassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('settings')
        else:
            messages.warning(request, 'There was an error changing your password!')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

def handler404(request):
    response = render(request, '4oh4.html', {})
    response.status_code= 404
    return response

def handler500(request):
    response = render(request, '500.html', {})
    response.status_code = 500
    return response

@login_required
def refreshBalances(request):
    exchange_accounts = models.ExchangeAccount.objects.filter(user=request.user)
    has_errors, errors = models.update_exchange_balances(exchange_accounts)
    if has_errors:
        for error in errors:
            messages.warning(request, error)
    return redirect('home')

def get_latest_exchange_balances(exchange_balances):
    latest_timestamp = exchange_balances.values(
        'currency'
    ).annotate(
        max_timestamp=Max('timestamp')
    ).order_by()

    q_statement = Q()
    for pair in latest_timestamp:
        q_statement |= (
            Q(currency__exact=pair['currency']) &
            Q(timestamp=pair['max_timestamp'])
        )

    return exchange_balances.filter(q_statement)

