from Logger import Logger
from ExchangeException import ExchangeException
import gdax

class GDAX:
    def __init__(self, key, secret, passphrase):
        self.client = gdax.AuthenticatedClient(key, secret, passphrase)
        self.logger = Logger(__name__)

    def getBalances(self):
        try:
            result = self.client.get_accounts()
            balances = {}

            for currency in result:
                name = currency["currency"].encode('utf-8').upper()
                value = float(currency["balance"].encode('utf-8'))

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e.message)

