# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import (
    REDIRECT_FIELD_NAME,
    login as auth_login,
    authenticate,
    update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Max, Q
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


@login_required
def home(request):
    exchange_accounts = models.ExchangeAccount.objects.filter(
        user=request.user)
    manual_inputs = models.ManualInput.objects.filter(user=request.user)

    if not exchange_accounts and not manual_inputs:
        return render(request, 'home.html', {'has_data': False})

    fiat = request.user.userprofile.fiat

    # get current rates
    market = Coinmarket()
    rates = market.getRates(fiat)
    balances = []
    other_balances = []
    crypto_balances = {}

    for exchange_account in exchange_accounts:
        exchange_balances = models.ExchangeBalance.objects.filter(
            exchange_account=exchange_account,
            most_recent=True
        )

        # aggregate latest balances
        for exchange_balance in exchange_balances:
            currency = exchange_balance.currency
            amount = exchange_balance.amount

            if currency in crypto_balances:
                crypto_balances[currency] += amount
            else:
                crypto_balances[currency] = amount

    for manual_input in manual_inputs:
        currency = manual_input.currency
        amount = manual_input.amount

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
    crypto_ydata = [x['amount'] for x in balances]
    fiat_ydata = [x['amount_fiat'] for x in balances]

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

    return render(
        request,
        'home.html',
        {
            'fiat': fiat,
            'balances': balances,
            'other_balances': other_balances,
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
                exchange_account=exchange_account,
                most_recent=True
            )

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
    if request.method == 'POST':
        form = forms.ManualInputForm(request.POST)
        if form.is_valid():
            manual_input = models.ManualInput(user=request.user)

            manual_input.currency = form.cleaned_data.get('currency').name
            manual_input.amount = form.cleaned_data.get('amount')

            manual_input.save()
            messages.success(request, 'Balance added successfully!')

            return redirect('manual_input')
        else:
            messages.warning(request, 'There was an error adding balance!')
    else:
        form = forms.ManualInputForm()
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
