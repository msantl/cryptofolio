from Logger import Logger
from ExchangeException import ExchangeException
from coinbase.wallet.client import Client

class Coinbase:
    def __init__(self, key, secret):
        self.client = Client(key, secret)
        self.logger = Logger(__name__)

    def getBalances(self):
        try:
            result = self.client.get_accounts()
            balances = {}

            for currency in result["data"]:
                name = currency["balance"]["currency"].encode('utf-8').upper()
                value = float(currency["balance"]["amount"].encode('utf-8'))

                if value > 0.0:
                    balances[name] = value

            return balances
        except Exception as e:
            self.logger.log(e)
            raise ExchangeException(self.__class__.__name__, e.message)

