# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class CryptofolioConfig(AppConfig):
    name = 'cryptofolio'

    def ready(self):
        from . import signals
