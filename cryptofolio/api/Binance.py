from binance.client import Client

from .Logger import Logger
from .ExchangeException import ExchangeException

class Binance:
    def __init__(self, key, secret):
        self.client = Client(key, secret)
        self.logger = Logger(__name__)

    def getBalances(self):
        try:
            result = self.client.get_account()
            balances = {}

            for currency in result['balances']:
                name = currency['asset'].encode('utf-8').upper()
                value = float(currency['free'].encode('utf-8'))

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

