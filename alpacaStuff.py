import keys
import time
import requests
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from alpaca.data.live import StockDataStream
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from alpaca.common import exceptions
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass

def showCryptoLivePrice(userStockQueryParam):
    # no keys required
    client = CryptoHistoricalDataClient()
    
    # single symbol request
    request_paramsCrypto = CryptoLatestQuoteRequest(symbol_or_symbols=[f'{userStockQueryParam}'])
    try:
        while True:
            # time.sleep(5)
            latest_quote = client.get_crypto_latest_quote(request_paramsCrypto)
            latest_ask_priceCrypto = latest_quote[f'{userStockQueryParam}'].ask_price
            print(f"{userStockQueryParam}: ${latest_ask_priceCrypto}",end="\r")
    # must use symbol to access even though it is single symbol
    except KeyboardInterrupt:
            print(f"\n{userStockQueryParam} : ${latest_ask_priceCrypto}")

def showStockLivePrice(userStockQueryParam):
    # # keys required for stock historical data client
    client = StockHistoricalDataClient(keys.KEY, keys.SECRET)

    request_params = StockLatestQuoteRequest(symbol_or_symbols=[f'{userStockQueryParam}'])
    symbol_quotes = client.get_stock_latest_quote(request_params)
    try:
        while True:
            # time.sleep(5)
            symbol_quotes = client.get_stock_latest_quote(request_params)
            latest_ask_price = symbol_quotes[f'{userStockQueryParam}'].ask_price
            print(f"{userStockQueryParam} : ${latest_ask_price}",end="\r")
    except KeyboardInterrupt:
            print(f"\n{userStockQueryParam} : ${latest_ask_price}")

# wss_client = StockDataStream(keys.KEY, keys.SECRET)

# # async handler
# async def quote_data_handler(data):
#     # quote data will arrive here
#     print(data)

# wss_client.subscribe_quotes(quote_data_handler, "AAPL")

# wss_client.run()

def main():
    trading_client = TradingClient(keys.KEY, keys.SECRET)

# search for crypto assets
    search_params = GetAssetsRequest(asset_class=AssetClass.CRYPTO)

    assets = trading_client.get_all_assets(search_params)
    # Adding all tradable crypto assets into a list so we can have one single if else statement to find the price for 
    # any asset, be it crypto or stocks.
    allCryptoSymbols = []
    for i in range(len(assets)):
        allCryptoSymbols.append(assets[i].symbol)
    userStockQueryParam = input("Enter the Ticker Symbol: ")
    if trading_client.get_asset(userStockQueryParam).tradable:
        showStockLivePrice(userStockQueryParam)
    elif userStockQueryParam in allCryptoSymbols:
        showCryptoLivePrice(userStockQueryParam)
    else:
        print("This particular security is not tradable or doesn't exist.")

main()