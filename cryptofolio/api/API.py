from Coinmarketcap import Coinmarket
from Binance import Binance
from Bittrex import Bittrex
from Coinbase import Coinbase
from Liqui import Liqui
from Poloniex import Poloniex

from Config import Config
from ExchangeException import ExchangeException

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
            key = self.exchange.key.encode('utf-8')
            secret = self.exchange.secret.encode('utf-8')
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

