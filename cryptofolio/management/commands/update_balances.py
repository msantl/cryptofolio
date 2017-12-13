from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from cryptofolio.models import (
    ExchangeAccount,
    ExchangeBalance,
    ManualInput,
    TimeSeries,
    update_exchange_balances,
    get_aggregated_balances)
from cryptofolio.api.Coinmarket import Coinmarket


class Command(BaseCommand):
    help = "Updates balances for all users on all exchanges"

    def handle(self, *args, **options):
        market = Coinmarket()
        users = User.objects.all()

        for user in users:
            self.stdout.write("Refreshing balances for %s" % (user.email))
            exchange_accounts = ExchangeAccount.objects.filter(user=user)
            has_errors, errors = update_exchange_balances(exchange_accounts)

            if has_errors:
                for error in errors:
                    self.stderr.write("%s %s" % (user.email, error))

            self.update_time_series(market, user)

    def update_time_series(self, market, user):
        self.stdout.write("Updating time series for %s" % (user.email))
        fiat = user.userprofile.fiat
        rates = market.getRates(fiat)
        exchange_accounts = ExchangeAccount.objects.filter(user=user)
        manual_inputs = ManualInput.objects.filter(user=user)
        total = 0

        crypto_balances = get_aggregated_balances(
            exchange_accounts, manual_inputs)

        for balance in crypto_balances:
            if balance in rates:
                total += crypto_balances[balance] * rates[balance]
            elif balance == fiat:
                total += crypto_balances[balance]

        entry = TimeSeries(user=user, amount=total, fiat=fiat)
        entry.save()
