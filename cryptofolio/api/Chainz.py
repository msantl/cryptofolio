import requests
from .Logger import Logger


class Chainz:
    def __init__(self):
        self.logger = Logger(__name__)

    def getBalance(self, address):
        req_url = ('https://chainz.cryptoid.info/ltc/api.dws'
                   '?q=getbalance&a=') + address
        try:
            response = requests.get(req_url)
            return response.json()
        except Exception as e:
            self.logger.log(e)
        return 0.0
