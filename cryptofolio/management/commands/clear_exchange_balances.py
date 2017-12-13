from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from cryptofolio.models import ExchangeAccount, ExchangeBalance


class Command(BaseCommand):
    help = "Remove ALL balances from ALL exchanges for ALL users"

    def handle(self, *args, **options):
        users = User.objects.all()

        for user in users:
            self.stdout.write("Removing balances for %s" % (user.email))
            exchange_accounts = ExchangeAccount.objects.filter(user=user)

            for exchange_account in exchange_accounts:
                exchange_balances = ExchangeBalance.objects.filter(
                    exchange_account=exchange_account)

                for exchange_balance in exchange_balances:
                    exchange_balance.delete()
