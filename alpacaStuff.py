import keys
import time
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

def getLivePriceAskAsset(trading_client):
    try:
        userStockQueryParam = input("Enter the Ticker Symbol: ")
        try:
            if trading_client.get_asset(userStockQueryParam).tradable:
                showStockLivePrice(userStockQueryParam)
        except:
                showCryptoLivePrice(userStockQueryParam)
    except:
            print("This particular security is not tradable or doesn't exist.")

def main():
    trading_client = TradingClient(keys.KEY, keys.SECRET)
    if (trading_client.get_clock().is_open):
        print("The market is open.")
        getLivePriceAskAsset(trading_client)
    else:
        print("The stock market is closed, crypto market is open.")
        getLivePriceAskAsset(trading_client)
main()