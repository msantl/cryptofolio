import requests
from .Logger import Logger


class Blockchair:
    def __init__(self):
        self.logger = Logger(__name__)

    def getBalance(self, address):
        req_url = ('https://api.blockchair.com/bitcoin-cash'
                   '/dashboards/address/') + address
        try:
            response = requests.get(req_url)
            return response.json()['data'][0]['sum_value_unspent']
        except Exception as e:
            self.logger.log(e)
        return 0.0
