from .Binance import Binance
from .Bittrex import Bittrex
from .Coinbase import Coinbase
from .Liqui import Liqui
from .Poloniex import Poloniex
from .GDAX import GDAX

from .Config import Config
from .ExchangeException import ExchangeException

class API:
    def __init__(self, exchange=None):
        self.exchange = exchange
        self.refreshBalances()

    def refreshBalances(self):
        self.balances = self.__getBalances()

    def __getBalances(self):
        balances = {}

        error = None

        if self.exchange:
            key, secret, passphrase = ('', '', '')

            if self.exchange.key:
                key = self.exchange.key

            if self.exchange.secret:
                secret = self.exchange.secret

            if self.exchange.passphrase:
                passphrase = self.exchange.passphrase

            api = None

            if self.exchange.exchange.name == Config.BINANCE:
                api = Binance(key, secret)
            elif self.exchange.exchange.name == Config.BITTREX:
                api = Bittrex(key, secret)
            elif self.exchange.exchange.name == Config.COINBASE:
                api = Coinbase(key, secret)
            elif self.exchange.exchange.name == Config.LIQUI:
                api = Liqui(key, secret)
            elif self.exchange.exchange.name == Config.POLONIEX:
                api = Poloniex(key, secret)
            elif self.exchange.exchange.name == Config.GDAX:
                api = GDAX(key, secret, passphrase)

            if api:
                try:
                    new_balances = api.getBalances()
                    for key in new_balances:
                        if key in balances:
                            balances[key] += new_balances[key]
                        else:
                            balances[key] = new_balances[key]
                except ExchangeException as e:
                    error = e.message
            else:
                error = "Exchange %s is not defined!" % (
                    self.exchange.exchange.name
                )

        return (balances, error)

    def getBalances(self):
        return self.balances

