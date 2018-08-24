import requests
from .Logger import Logger


class Ripple:
    def __init__(self):
        self.logger = Logger(__name__)

    def getBalance(self, address):
        req_url = ('https://data.ripple.com'
                   '/v2/accounts/{}/balances'.format(address,))
        try:
            response = requests.get(req_url)
            xrp_balance = next((item for item in response.json()['balances']
                                        if item["currency"] == "XRP"), None)
            return xrp_balance['value']

        except Exception as e:
            self.logger.log(e)
        return 0.0
