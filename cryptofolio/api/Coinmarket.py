from coinmarketcap import Market
from ratelimit import limits, sleep_and_retry

from .Logger import Logger

class Coinmarket:
    def __init__(self):
        self.logger = Logger(__name__)
        self.market = Market()

    # Coinmarketcap API is limited to:
    # Please limit requests to no more than 30 per minute.
    @sleep_and_retry
    @limits(calls=27, period=60)
    def getMarket(self):
        return self.market

    def getRates(self, fiat):
        market = {}
        start = 0
        limit = 100

        while True:
            try:
                ticker = self.getMarket().ticker(
                        start=start, limit=limit, sort='id', convert=fiat)
            except TypeError as e:
                # This happens when we issue more requests than allowed
                self.logger.log(e)
                break

            if ticker['data'] == None:
                break

            for i in ticker['data']:
                t = ticker['data'][i]
                name = t['name'].upper()
                symbol = t['symbol'].upper()
                price = t['quotes'][fiat]['price']
                if price:
                    market[name] = float(price)
                    market[symbol] = float(price)

            start += limit
        return market

    def getCoinNames(self):
        listings = self.getMarket().listings()
        coins = []
        for coin in listings['data']:
            coins.append(coin['symbol'])
        return coins

