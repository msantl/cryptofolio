# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import (
    REDIRECT_FIELD_NAME,
    login as auth_login,
    authenticate,
    update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.template import RequestContext
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from . import forms
from . import models

from .api.Coinmarket import Coinmarket

import time
import datetime


@login_required
def home(request):
    fiat = request.user.userprofile.fiat
    exchange_accounts = models.ExchangeAccount.objects.filter(
        user=request.user)
    manual_inputs = models.ManualInput.objects.filter(user=request.user)

    if not exchange_accounts and not manual_inputs:
        return render(request, 'home.html', {'has_data': False})

    # get current rates
    market = Coinmarket()
    rates = market.getRates(fiat)
    balances = []
    other_balances = []
    crypto_balances = models.get_aggregated_balances(
        exchange_accounts, manual_inputs)

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
        elif currency == fiat:
            balances.append(
                {
                    'currency': currency,
                    'amount': crypto_balances[currency],
                    'amount_fiat': crypto_balances[currency],
                }
            )
        else:
            other_balances.append(
                {
                    'currency': currency,
                    'amount': crypto_balances[currency]
                }
            )

    xdata = [x['currency'] for x in balances]
    fiat_ydata = [x['amount_fiat'] for x in balances]
    extra_serie = {
        "tooltip": {"y_start": "", "y_end": " " + fiat},
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

    # time series
    user_time_series = models.TimeSeries.objects.filter(
        user=request.user, fiat=fiat)

    def to_timestamp(x): return int(time.mktime(x.timetuple()) * 1000)
    xdata = [to_timestamp(entry.timestamp) for entry in user_time_series]
    ydata = [entry.amount for entry in user_time_series]

    time_series = {
        'charttype': "lineChart",
        'chartcontainer': 'time_series_container',
        'chartdata': {
            'x': xdata,
            'name1': 'Balance',
            'y1': ydata,
            'extra1': {
                "tooltip": {
                    "y_start": "You had ",
                    "y_end": fiat
                },
            }
        },
        'extra': {
            'x_is_date': True,
            "x_axis_format": "%d %b %H:%M",
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
            'other_balances': other_balances,
            'fiat_sum': sum(fiat_ydata),
            'has_data': True,
            'fiat_piechart': fiat_piechart,
            'time_series': time_series,
        }
    )


@login_required
def settings(request):
    exchanges = models.Exchange.objects.all()
    return render(request, 'settings.html', {'exchanges': exchanges})


@login_required
def exchange(request, exchange_id):
    exchange = get_object_or_404(models.Exchange, pk=exchange_id)
    exchange_balances = None
    stored_credentials = True

    if request.method == 'POST':
        form = forms.ExchangeAccountForm(request.POST)
        if form.is_valid():
            exchange_account, created = models.ExchangeAccount.objects.get_or_create(
                user=request.user,
                exchange=exchange
            )
            exchange_account.key = form.cleaned_data.get('key')
            exchange_account.secret = form.cleaned_data.get('secret')
            exchange_account.passphrase = form.cleaned_data.get('passphrase')

            exchange_account.save()
            has_errors, errors = models.update_exchange_balances(
                [exchange_account])

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
                exchange_account=exchange_account)

            form = forms.ExchangeAccountForm(instance=exchange_account)
        except ObjectDoesNotExist:
            form = forms.ExchangeAccountForm()
            stored_credentials = False

    return render(
        request,
        'exchange.html',
        {
            'form': form,
            'exchange': exchange,
            'stored_credentials': stored_credentials,
            'balances': exchange_balances
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
            auth_login(request, user)
            return redirect('home')
    else:
        form = forms.SignUpForm()

    return render(request, 'signup.html', {'form': form})


@login_required
@transaction.atomic
def change_details(request):
    if request.method == 'POST':
        form = forms.UserChangeDetailsForm(request.POST, instance=request.user)
        fiat_form = forms.UserChangeFiatForm(
            request.POST,
            instance=request.user.userprofile
        )
        if form.is_valid() and fiat_form.is_valid():
            form.save()
            fiat_form.save()
            messages.success(
                request, 'Your details were successfully updated!')
            return redirect('settings')
        else:
            messages.warning(
                request, 'There was an error changing your details!')
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
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('settings')
        else:
            messages.warning(
                request, 'There was an error changing your password!')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})


def handler404(request):
    response = render(request, '4oh4.html', {})
    response.status_code = 404
    return response


def handler500(request):
    response = render(request, '500.html', {})
    response.status_code = 500
    return response


@login_required
def refresh_balances(request):
    exchange_accounts = models.ExchangeAccount.objects.filter(
        user=request.user)
    has_errors, errors = models.update_exchange_balances(exchange_accounts)
    if has_errors:
        for error in errors:
            messages.warning(request, error)
    return redirect('settings')


@login_required
def remove_exchange(request, exchange_id):
    exchange = get_object_or_404(models.Exchange, pk=exchange_id)

    try:
        exchange_account = models.ExchangeAccount.objects.get(
            user=request.user,
            exchange=exchange
        )

        exchange_account.delete()
        messages.success(request, 'Exchange removed!')

    except ObjectDoesNotExist:
        messages.warning(
            request, 'There was an error removing exchange from your account!')

    return redirect('exchange', exchange_id=exchange_id)


@login_required
def remove_balances(request):
    try:
        exchange_accounts = models.ExchangeAccount.objects.filter(
            user=request.user)
        for exchange_account in exchange_accounts:
            exchange_account.delete()
        messages.success(request, 'Balances removed!')
    except Exception as e:
        messages.warning(
            request, 'There was an error removing balances from your account!')
    return redirect('settings')


def policy(request):
    return render(request, 'policy.html', {})


def get_latest_exchange_balances(exchange_balances):
    return exchange_balances.filter(most_recent=True)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    redirect_to = request.GET.get(REDIRECT_FIELD_NAME, '')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(django_settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
        else:
            messages.warning(request, 'Wrong username and/or password!')
    else:
        form = AuthenticationForm(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        REDIRECT_FIELD_NAME: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }

    return render(request, 'login.html', context)


@login_required
def manual_input(request):
    manual_input = models.ManualInput(user=request.user)
    balances = []

    if request.method == 'POST':
        form = forms.ManualInputForm(request.POST, instance=manual_input)
        if form.is_valid():
            form.save()
            messages.success(request, 'Balance added successfully!')
            return redirect('manual_input')
        else:
            messages.warning(request, 'There was an error adding balance!')
    else:
        form = forms.ManualInputForm(instance=manual_input)
        balances = models.ManualInput.objects.filter(user=request.user)

    context = {
        'form': form,
        'balances': balances
    }
    return render(request, 'manual.html', context)


@login_required
def remove_manual_input(request, manual_input_id):
    try:
        manual_input = models.ManualInput.objects.filter(
            user=request.user,
            id=manual_input_id
        )

        manual_input.delete()
        messages.success(request, 'Balance removed!')

    except ObjectDoesNotExist:
        messages.warning(
            request, 'There was an error removing balance from your account!')

    return redirect('manual_input')
