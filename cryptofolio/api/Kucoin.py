from kucoin.client import Client

from .Config import Config
from .Logger import Logger
from .ExchangeException import ExchangeException


class Kucoin:
    def __init__(self, key, secret):
        self.logger = Logger(__name__)

        try:
            self.client = Client(key, secret)
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

    def getBalances(self):
        try:
            result = self.client.get_all_balances()
            balances = {}

            for currency in result:
                name = currency['coinType'].upper()
                value = float(currency['balance'])

                if value > Config.BALANCE_ZERO:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
