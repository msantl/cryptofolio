from coinbase.wallet.client import Client

from .Logger import Logger
from .ExchangeException import ExchangeException


class Coinbase:
    def __init__(self, key, secret):
        self.logger = Logger(__name__)

        try:
            self.client = Client(key, secret)
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

    def getBalances(self):
        try:
            result = self.client.get_accounts()
            balances = {}

            for currency in result["data"]:
                name = currency["balance"]["currency"].upper()
                value = float(currency["balance"]["amount"])

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
