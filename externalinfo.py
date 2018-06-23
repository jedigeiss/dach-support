#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 00:01:51 2018

@author: jan
"""

from coinmarketcap import Market
import json
from weather import Weather, Unit


def getweather(city):
    weather = Weather(unit=Unit.CELSIUS)
    location = weather.lookup_by_location(city)
    condition = location.condition
    forecasts = location.forecast
    return condition, forecasts


def getprice(coin):
    coinmarketcap = Market()
    default = "Bitcoin"
    
    if len(coin) == 0:
        coin = default
    elif coin.upper() == "SBD":
        coin = "steem-dollars" 
    
    #get the marketdata via api from coinmarketcap
    marketdata = coinmarketcap.ticker(coin, convert='EUR')
    marketdata = str(marketdata)
    marketdata = marketdata.replace("'", "\"")
    marketdata = marketdata.replace("False","\"False\"")
    marketdata = marketdata.replace("None","\"None\"")
    marketdata = marketdata.replace("True","\"True\"")
    found = marketdata.find("error")
    if (found > -1): # Coinmarketcap replied with a coin not found error
        return -1
    else:
        marketdata = marketdata[1:(len(marketdata)-1)]
        #loading the data with json and extractint what we need
        parseddata = json.loads(marketdata)
        priceusd = parseddata["price_usd"]
        priceeur = parseddata["price_eur"]
        pricebtc = parseddata["price_btc"]
        name = parseddata["name"]
        change1h = parseddata["percent_change_1h"]
        change24h = parseddata["percent_change_24h"]
        change7d = parseddata["percent_change_7d"]
        return [priceusd, priceeur, pricebtc, name, change1h, change24h, change7d]