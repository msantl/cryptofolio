from coinmarketcap import Market

class Coinmarket:
    def __init__(self):
        self.market = Market()

    def getRates(self, fiat):
        ticker = self.market.ticker(convert=fiat)
        market = {}

        for t in ticker:
            currency = t['symbol'].upper()
            price_key = ("price_" + fiat).lower()
            if t[price_key]:
                market[currency] = float(t[price_key])

        return market

