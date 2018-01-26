from pyetherscan import Client

from .Logger import Logger


class Etherscan:
    def __init__(self):
        self.logger = Logger(__name__)
        try:
            self.client = Client()
        except Exception as e:
            self.logger.log(e)

    def getBalance(self, address):
        try:
            result = self.client.get_single_balance(address)
            if result.message == 'OK':
                return result.balance / 1000000000000000000

        except Exception as e:
            self.logger.log(e)

        return 0.0
