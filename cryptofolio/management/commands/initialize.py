from django.core.management.base import BaseCommand

from cryptofolio.models import Fiat
from cryptofolio.models import Currency
from cryptofolio.models import Exchange
from cryptofolio.api.Coinmarket import Coinmarket
from cryptofolio.api.Config import get_configured_exchange_names
from cryptofolio.api.Config import get_configured_fiat_names

class Command(BaseCommand):
    help = "Import coin names from Coinmarketcap"

    def handle(self, *args, **options):
        market = Coinmarket()
        for name in market.getCoinNames():
            coin, _ = Currency.objects.get_or_create(name=name)

        for name in get_configured_fiat_names():
            coin, _ = Fiat.objects.get_or_create(name=name)

        for name in get_configured_exchange_names():
            exchange, _ = Exchange.objects.get_or_create(name=name)

