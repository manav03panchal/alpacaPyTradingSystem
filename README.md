# alpacaPyTradingSystem

An attempt at making a standalone all-in-one paper trading GUI using pyQt6 and the Alpaca-py SDK. (https://github.com/alpacahq/alpaca-py)
It was supposed to provide the user with live asking price of an equity traded on the US Markets, as well as Crypto/USD Prices.
Users could also see the graph, as well as place orders, all managed by the SDK's Trading API.

# To run this project

Get keys from Alpaca.com, make a file called "keys.py" and open gui.py and run.
Internet connection is required.

# Current Issues

The live quote/asset-price function works, but implementing charting functionality as well as an order placement utility seems cumbersome
and frankly speaking, almost impossible with the resources at hand.

# Future Work

Will migrate the logic into making a web-app using a different language and tech stack

