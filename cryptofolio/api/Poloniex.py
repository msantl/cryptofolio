from poloniex import Poloniex as Client

from .Logger import Logger
from .ExchangeException import ExchangeException


class Poloniex:
    def __init__(self, key, secret):
        self.logger = Logger(__name__)

        try:
            self.client = Client(key, secret)
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

    def getBalances(self):
        try:
            result = self.client.returnBalances()
            balances = {}

            for currency in result:
                name = currency.encode('utf-8').upper()
                value = float(result[currency])

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
