from .Binance import Binance
from .Bittrex import Bittrex
from .Coinbase import Coinbase
from .CoinbasePro import CoinbasePro
from .Kraken import Kraken
from .Kucoin import Kucoin
from .Poloniex import Poloniex

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

                if self.exchange.exchange.label == Config.BINANCE:
                    api = Binance(key, secret)
                elif self.exchange.exchange.label == Config.BITTREX:
                    api = Bittrex(key, secret)
                elif self.exchange.exchange.label == Config.COINBASE:
                    api = Coinbase(key, secret)
                elif self.exchange.exchange.label == Config.POLONIEX:
                    api = Poloniex(key, secret)
                elif self.exchange.exchange.label == Config.COINBASEPRO:
                    api = CoinbasePro(key, secret, passphrase)
                elif self.exchange.exchange.label == Config.KRAKEN:
                    api = Kraken(key, secret)
                elif self.exchange.exchange.label == Config.KUCOIN:
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
                        self.exchange.exchange.label)

            except ExchangeException as e:
                error = e.message

        return (balances, error)

    def getBalances(self):
        return self.balances
