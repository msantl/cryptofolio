# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from django.contrib.auth.models import User
from . import models


def create_test_user():
    return User(username="test", password="test")


def create_test_exchange():
    return models.Exchange(name="TEST")


def get_test_key():
    return "123"


def get_test_secret():
    return "321"


def get_test_passphrase():
    return "abc"


def get_test_currency():
    return "BTC"


def get_test_amount():
    return "123.456789"


class UserProfileTests(TestCase):
    def test_create(self):
        test_user = create_test_user()
        test_fiat = get_test_currency()

        user_profile = models.UserProfile(
            user=test_user,
            fiat=test_fiat
        )

        self.assertEqual(user_profile.user, test_user)
        self.assertEqual(user_profile.fiat, test_fiat)


class ExchangeAccountTests(TestCase):
    def test_create_empty_passphrase(self):
        test_user = create_test_user()
        test_exchange = create_test_exchange()
        test_key = get_test_key()
        test_secret = get_test_secret()
        exchange_account = models.ExchangeAccount(
            user=test_user,
            exchange=test_exchange,
            key=test_key,
            secret=test_secret,
        )

        self.assertEqual(exchange_account.user, test_user)
        self.assertEqual(exchange_account.exchange, test_exchange)
        self.assertEqual(exchange_account.key, test_key)
        self.assertEqual(exchange_account.secret, test_secret)
        self.assertEqual(exchange_account.passphrase, None)

    def test_create_with_passphrase(self):
        test_user = create_test_user()
        test_exchange = create_test_exchange()
        test_key = get_test_key()
        test_secret = get_test_secret()
        test_passphrase = get_test_passphrase()
        exchange_account = models.ExchangeAccount(
            user=test_user,
            exchange=test_exchange,
            key=test_key,
            secret=test_secret,
            passphrase=test_passphrase,
        )

        self.assertEqual(exchange_account.user, test_user)
        self.assertEqual(exchange_account.exchange, test_exchange)
        self.assertEqual(exchange_account.key, test_key)
        self.assertEqual(exchange_account.secret, test_secret)
        self.assertEqual(exchange_account.passphrase, test_passphrase)


class ExchangeBalanceTests(TestCase):
    def test_create(self):
        exchange_account = models.ExchangeAccount(
            user=create_test_user(),
            exchange=create_test_exchange(),
            key=get_test_key(),
            secret=get_test_secret(),
        )

        test_currency = get_test_currency()
        test_amount = get_test_amount()

        exchange_balance = models.ExchangeBalance(
            exchange_account=exchange_account,
            currency=test_currency,
            amount=test_amount,
        )

        self.assertEqual(exchange_balance.currency, test_currency)
        self.assertEqual(exchange_balance.amount, test_amount)
