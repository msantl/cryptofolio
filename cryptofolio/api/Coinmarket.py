from coinmarketcap import Market


class Coinmarket:
    def __init__(self):
        self.market = Market()

    def getRates(self, fiat):
        ticker = self.market.ticker(limit=0, convert=fiat)
        market = {}

        for t in ticker:
            name = t['symbol'].upper()
            symbol = t['name'].upper()
            price_key = ("price_" + fiat).lower()
            if t[price_key]:
                market[name] = float(t[price_key])
                market[symbol] = float(t[price_key])

        return market

    def convertToFiat(self, crypto_balances, fiat):
        balances = []
        other_balances = []
        rates = self.getRates(fiat)
        for currency in crypto_balances:
            if currency in rates:
                balances.append(
                    {
                        'currency': currency,
                        'amount': crypto_balances[currency],
                        'amount_fiat': crypto_balances[currency] * rates[currency],
                    }
                )
            elif currency == fiat:
                balances.append(
                    {
                        'currency': currency,
                        'amount': crypto_balances[currency],
                        'amount_fiat': crypto_balances[currency],
                    }
                )
            else:
                other_balances.append(
                    {
                        'currency': currency,
                        'amount': crypto_balances[currency]
                    }
                )

        return (balances, other_balances)
