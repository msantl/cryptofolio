class Config:
    BINANCE="Binance"
    BITTREX="Bittrex"
    COINBASE="Coinbase"
    LIQUI="Liqui"
    POLONIEX="Poloniex"
    GDAX="GDAX"
    KRAKEN="Kraken"
    KUCOIN="Kucoin"

    BALANCE_ZERO=0.00000001

def get_configured_exchange_names():
        return [Config.BINANCE, Config.BITTREX, Config.COINBASE, Config.LIQUI,
                Config.POLONIEX, Config.GDAX, Config.KRAKEN, Config.KUCOIN]

def get_configured_fiat_names():
    return ["USD", "EUR", "GBP"]

def get_default_fiat_name():
    return get_configured_fiat_names()[0]
