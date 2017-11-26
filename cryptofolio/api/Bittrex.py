from bittrex import Bittrex as Client

from .Logger import Logger
from .ExchangeException import ExchangeException

class Bittrex:
    def __init__(self, key, secret):
        self.client = Client(bytes(key, 'utf-8'), bytes(secret, 'utf-8'))
        self.logger = Logger(__name__)

    def getBalances(self):
        try:
            result = self.client.get_balances()
            balances = {}

            if not result['success']:
                raise ExchangeException(self.__class__.__name__, result['message'])

            for currency in result["result"]:
                name = currency["Currency"].encode('utf-8').upper()
                value = currency["Balance"]

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
