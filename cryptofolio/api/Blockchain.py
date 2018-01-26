import requests
from time import sleep

from .Logger import Logger


class Blockchain:
    def __init__(self):
        self.logger = Logger(__name__)

    def getBalance(self, address):
        req_url = 'https://blockchain.info/q/addressbalance/' + address
        try:
            response = requests.get(req_url)
            return response.json() / 100000000
        except Exception as e:
            self.logger.log(e)
        return 0.0
