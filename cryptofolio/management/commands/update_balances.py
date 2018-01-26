from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone

from cryptofolio.models import (
    ExchangeAccount,
    ExchangeBalance,
    ManualInput,
    AddressInput,
    BalanceTimeSeries,
    TimeSeries,
    update_exchange_balances,
    update_address_input_balances,
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

            update_address_input_balances(user)
            self.update_time_series(market, user)

    def update_time_series(self, market, user):
        self.stdout.write("Updating time series for %s" % (user.email))
        fiat = user.userprofile.fiat
        exchange_accounts = ExchangeAccount.objects.filter(user=user)
        manual_inputs = ManualInput.objects.filter(user=user)
        address_inputs = AddressInput.objects.filter(user=user)

        crypto_balances = get_aggregated_balances(
            exchange_accounts, manual_inputs, address_inputs)
        balances, _ = market.convertToFiat(crypto_balances, fiat)
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
