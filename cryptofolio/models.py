# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField

from api.API import API

class Currency(models.Model):
    name = models.CharField(max_length=10, primary_key=True)

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
    exchangeAccount = models.ForeignKey(ExchangeAccount, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50)
    amount = models.FloatField(default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s %s %s" %  (
                self.exchangeAccount,
                self.currency,
                self.timestamp)

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
            for currency in balances:
                exchange_balance = ExchangeBalance(
                    exchangeAccount=exchange_account,
                    currency=currency,
                    amount=balances[currency]
                )
                exchange_balance.save()

    return (has_errors, errors)


