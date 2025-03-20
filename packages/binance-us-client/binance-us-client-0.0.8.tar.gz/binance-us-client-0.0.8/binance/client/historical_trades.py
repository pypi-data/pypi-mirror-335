"""
get historical trades
"""

from base_api import binanceus_get_without_signature, HISTORICAL_TRADES

import requests
API_URL = "https://api.binance.us"
HISTORICAL_TRADES = "/api/v3/historicalTrades"


def binanceus_get_without_signature(uri_path, data, api_key):
    """
    binance get request
    """
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    params={
        **data,
    }
    resp = requests.get((API_URL + uri_path), params=params, headers=headers)
    return resp.json()


def get_historical_trades(symbol: str, api_key: str, from_id: int = None, limit: int = 1000):
    data = {
        "symbol": symbol,
        "fromId": from_id,
        "limit": limit,
    }
    result = binanceus_get_without_signature(HISTORICAL_TRADES, data, api_key)
    print(result)


if __name__ == '__main__':
    api_key_ = '<api key>'
    trades = get_historical_trades('BTCUSDT', api_key_, from_id=29517667)
    ...
