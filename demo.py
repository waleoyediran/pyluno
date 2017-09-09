from __future__ import print_function

import os

from pyluno.api import Luno


def runDemo():
    user = ''
    password = ''
    auth = 'BITX_KEY' in os.environ and 'BITX_SECRET' in os.environ
    if auth:
        user = os.environ['BITX_KEY']
        password = os.environ['BITX_SECRET']
    else:
        print("Note: Couldn't find a BITX_KEY environment variable."
              " This means that none of the API queries that"
              " require authentication will work."
              " Carrying on anyway, but make sure your"
              " credentials are available "
              " in the BITX_KEY and BITX_SECRET environment variables"
              " and run this demo again")
    api = Luno(user, password)
    print(api.market.get_ticker())
    print(api.market.get_all_tickers())
    print(api.market.get_order_book(5))
    print(api.market.get_trades(10))
    if auth:
        print(api.get_orders())
        print(api.get_funding_address('XBT'))
        print(api.get_balance())


if __name__ == '__main__':
    runDemo()
