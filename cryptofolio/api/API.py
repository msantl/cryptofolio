from .Binance import Binance
from .Bittrex import Bittrex
from .Coinbase import Coinbase
from .Liqui import Liqui
from .Poloniex import Poloniex
from .GDAX import GDAX
from .Kraken import Kraken
from .Kucoin import Kucoin

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
            try:
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
                elif self.exchange.exchange.name == Config.KRAKEN:
                    api = Kraken(key, secret)
                elif self.exchange.exchange.name == Config.KUCOIN:
                    api = Kucoin(key, secret)

                if api:
                    new_balances = api.getBalances()
                    for key in new_balances:
                        if key in balances:
                            balances[key] += new_balances[key]
                        else:
                            balances[key] = new_balances[key]
                else:
                    error = "Exchange %s is not defined!" % (
                        self.exchange.exchange.name)

            except ExchangeException as e:
                error = e.message

        return (balances, error)

    def getBalances(self):
        return self.balances
