from .Blockchain import Blockchain
from .Etherscan import Etherscan
from .Chainz import Chainz
from .Blockchair import Blockchair
from .Ripple import Ripple
from .Logger import Logger

from time import sleep

class BalanceFromAddress:
    def __init__(self):
        self.logger = Logger(__name__)
        self.handlers = {
            'BTC': Blockchain(),
            'ETH': Etherscan(),
            'LTC': Chainz(),
            'BCH': Blockchair(),
            'XRP': Ripple()
        }

    def getSingleBalance(self, currency, address):
        if currency in self.handlers:
            return self.handlers[currency].getBalance(address)
        return 0.0

    def getBalances(self, address_inputs):
        result = {}
        for i, a in enumerate(address_inputs):
            result[a.address] = self.getSingleBalance(a.currency, a.address)
            # poor man rate limiter
            if (i + 1) % 5 == 0:
                sleep(1)
        return result

    def getSupportedCurrencies():
        supported_currencies = ['BTC', 'ETH', 'LTC', 'BCH', 'XRP']
        return zip(supported_currencies, supported_currencies)
