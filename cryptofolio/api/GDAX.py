from gdax import AuthenticatedClient as Client

from .Config import Config
from .Logger import Logger
from .ExchangeException import ExchangeException


class GDAX:
    def __init__(self, key, secret, passphrase):
        self.logger = Logger(__name__)

        try:
            self.client = Client(key, secret, passphrase)
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)

    def getBalances(self):
        try:
            result = self.client.get_accounts()
            balances = {}

            if 'message' in result:
                raise Exception(result['message'])

            for currency in result:
                name = currency["currency"].upper()
                value = float(currency["balance"])

                if value >= Config.BALANCE_ZERO:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e)
