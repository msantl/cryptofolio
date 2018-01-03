# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField

from .api.API import API


class Currency(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    crypto = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fiat = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return "%s %s" % (self.user, self.fiat)


class Exchange(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class ExchangeAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    key = EncryptedCharField(max_length=1024)
    secret = EncryptedCharField(max_length=1024)
    passphrase = EncryptedCharField(
        max_length=1024,
        default=None,
        blank=True,
        null=True,
        help_text='<ul><li>Optional</li></ul>')

    def __str__(self):
        return "%s %s" % (self.user.username, self.exchange.name)


class ExchangeBalance(models.Model):
    exchange_account = models.ForeignKey(
        ExchangeAccount,
        on_delete=models.CASCADE
    )
    currency = models.CharField(max_length=10)
    amount = models.FloatField(default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s %s" % (
            self.exchange_account,
            self.currency,
            self.timestamp)


class ManualInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=10)
    amount = models.FloatField(default=None, blank=True, null=True)

    def __str__(self):
        return "%s %s %s %s" % (self.user.username, self.timestamp,
                                self.currency, self.amount)


class TimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    amount = models.FloatField(default=None, blank=True, null=True)
    fiat = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return "%s %s %s %s" % (self.user.username, self.timestamp,
                                self.amount, self.fiat)


class BalanceTimeSeries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    amount = models.FloatField(default=None, blank=True, null=True)
    currency = models.CharField(max_length=10, default='BTC')
    fiat = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return "%s %s %s %s" % (self.user.username, self.timestamp,
                                self.amount, self.currency)


def update_exchange_balances(exchange_accounts):
    has_errors = False
    errors = []
    for exchange_account in exchange_accounts:
        api = API(exchange_account)
        balances, error = api.getBalances()

        if error:
            has_errors = True
            errors.append(error)
        else:
            exchange_balances = ExchangeBalance.objects.filter(
                exchange_account=exchange_account)

            for currency in balances:
                exchange_balance, created = ExchangeBalance.objects.get_or_create(
                    exchange_account=exchange_account,
                    currency=currency)

                exchange_balance.amount = balances[currency]
                exchange_balance.save()

            for exchange_balance in exchange_balances:
                currency = exchange_balance.currency
                if currency not in balances:
                    exchange_balance.delete()


    return (has_errors, errors)


def get_aggregated_balances(exchange_accounts, manual_inputs):
    crypto_balances = {}
    for exchange_account in exchange_accounts:
        exchange_balances = ExchangeBalance.objects.filter(
            exchange_account=exchange_account)

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

    return crypto_balances
