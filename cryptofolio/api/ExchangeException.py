class ExchangeException(Exception):
    def __init__(self, exchange, message):
        super(ExchangeException, self).__init__(message)
        self.message = "%s: %s" % (exchange, message)
