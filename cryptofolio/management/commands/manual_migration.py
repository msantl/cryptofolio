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
        for name in get_configured_exchange_names():
            exchange, _ = Exchange.objects.get_or_create(name=name)
            exchange.label = name
            exchange.save()
