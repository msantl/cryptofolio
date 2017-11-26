from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from cryptofolio.models import ExchangeAccount, update_exchange_balances

class Command(BaseCommand):
    help = "Updates balances for all users on all exchanges"

    def handle(self, *args, **options):
        users = User.objects.all()

        for user in users:
            self.stdout.write("Refreshing balances for %s" % (user.email))
            exchange_accounts = ExchangeAccount.objects.filter(user=user)
            has_errors, errors = update_exchange_balances(exchange_accounts)

            if has_errors:
                for error in errors:
                    self.stderr.write("%s %s" % (user.email, error))


