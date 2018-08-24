from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone

from cryptofolio.models import (
    AddressInput,
    BalanceTimeSeries,
    Currency,
    Fiat,
    ExchangeAccount,
    ExchangeBalance,
    ManualInput,
    Rates,
    TimeSeries,
    convert_to_fiat,
    get_aggregated_balances,
    update_exchange_balances,
    update_address_input_balances)
from cryptofolio.api.Coinmarket import Coinmarket


class Command(BaseCommand):
    help = "Updates balances for all users on all exchanges"

    def handle(self, *args, **options):
        users = User.objects.all()
        market = Coinmarket()

        currencies = Currency.objects.all()
        fiats = Fiat.objects.all()

        # update rates
        for fiat in fiats:
            rates = market.getRates(fiat.name)
            for currency in currencies:
                if currency.name in rates:
                    rate, _ = Rates.objects.get_or_create(
                        currency=currency.name, fiat=fiat.name)
                    rate.rate = rates[currency.name]
                    rate.save()

        for user in users:
            self.stdout.write("Refreshing balances for %s" % (user.email))
            exchange_accounts = ExchangeAccount.objects.filter(user=user)
            has_errors, errors = update_exchange_balances(exchange_accounts)

            if has_errors:
                for error in errors:
                    self.stderr.write("%s %s" % (user.email, error))

            update_address_input_balances(user)
            self.update_time_series(user)

    def update_time_series(self, user):
        fiat = user.userprofile.fiat
        exchange_accounts = ExchangeAccount.objects.filter(user=user)
        manual_inputs = ManualInput.objects.filter(user=user)
        address_inputs = AddressInput.objects.filter(user=user)

        crypto_balances = get_aggregated_balances(
            exchange_accounts, manual_inputs, address_inputs)

        balances, _ = convert_to_fiat(crypto_balances, fiat)
        total = 0

        # this way all TimeSeries will have the same timestamp
        now = timezone.now()

        for balance in balances:
            total += balance['amount_fiat']
            entry = BalanceTimeSeries(
                user=user, amount=balance['amount_fiat'],
                currency=balance['currency'], fiat=fiat, timestamp=now)
            entry.save()

        entry = TimeSeries(user=user, amount=total, fiat=fiat)
        entry.save()
