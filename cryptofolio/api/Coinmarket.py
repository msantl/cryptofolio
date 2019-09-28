import json

from django.conf import settings
from coinmarketcap import Market
from ratelimit import limits, sleep_and_retry
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from .Logger import Logger

class Coinmarket:
    PRODUCTION_BASE_URL = 'https://pro-api.coinmarketcap.com/v1/'
    TICKER_PATH = 'cryptocurrency/listings/latest'
    LISTINGS_PATH = 'cryptocurrency/map'

    def __init__(self, is_sandbox=True):
        self.logger = Logger(__name__)
        self.session = Session()
        headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': settings.COINMARKET_API_KEY
        }
        self.session.headers.update(headers)

    # Coinmarketcap API is limited:
    # Please limit requests to no more than 30 per minute.
    @sleep_and_retry
    @limits(calls=27, period=60)
    def fetch(self, path, params=None):
        try:
            response = self.session.get(
                    '{}{}'.format(self.PRODUCTION_BASE_URL, path),
                    params=params)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.logger.log(e)

    def getRates(self, fiat):
        market = {}

        parameters = {'start': '1', 'limit': '1000', 'convert': fiat}
        ticker = self.fetch(self.TICKER_PATH, params=parameters)

        for t in ticker['data']:
            name = t['name'].upper()
            symbol = t['symbol'].upper()
            price = t['quote'][fiat]['price']
            if price:
                market[name] = float(price)
                market[symbol] = float(price)

        return market

    def getCoinNames(self):
        parameters = {'start': '1', 'limit': '4710'}
        listings = self.fetch(self.LISTINGS_PATH, params=parameters)
        coins = []
        for coin in listings['data']:
            coins.append(coin['symbol'])
        return coins

