from .Logger import Logger
from .ExchangeException import ExchangeException

from krakenex import API as Client


class Kraken:
    def __init__(self, key, secret):
        self.logger = Logger(__name__)

        try:
            self.client = Client(key, secret)
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

    def getBalances(self):
        try:
            result = self.client.query_private('Balance')
            balances = {}

            error = result['error']
            if len(error) > 0:
                raise Exception(', '.join(error))

            balance = result['result']
            for currency in balance:
                # remove first symbol ('Z' or 'X')
                name_trimmed = currency[1:] if len(currency) == 4 else currency

                name = name_trimmed.upper()
                value = float(balance[currency])

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
