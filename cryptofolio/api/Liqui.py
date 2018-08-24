from liqui import Liqui as Client

from .Config import Config
from .Logger import Logger
from .ExchangeException import ExchangeException


class Liqui:
    def __init__(self, key, secret):
        self.logger = Logger(__name__)

        try:
            self.client = Client(key, secret)
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

    def getBalances(self):
        try:
            result = self.client.balances()
            balances = {}

            for currency in result.keys():
                name = currency.upper()
                value = float(result[currency])

                if value > Config.BALANCE_ZERO:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
