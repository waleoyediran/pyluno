"""Markets module."""
import logging

import pandas as pd

log = logging.getLogger(__name__)


class Market(object):
    """Market related methods."""

    def __init__(self, main):
        """Initialise with super's main."""
        self.main = main

    def get_ticker(self, kind='auth', pair=None):
        """Get the latest ticker indicator for a pair."""
        params = {'pair': self.main.pair if pair is None else pair}
        return self.main.api_request('ticker', params, kind=kind)

    def get_all_tickers(self, kind='auth'):
        """Get all the latest ticker indicators."""
        return self.main.api_request('tickers', None, kind=kind)

    def get_order_book(self, limit=None, kind='auth', pair=None):
        """Get a list of bids and asks in the order book."""
        params = {'pair': self.main.pair if pair is None else pair}
        orders = self.main.api_request('orderbook', params, kind=kind)
        if limit is not None:
            orders['bids'] = orders['bids'][:limit]
            orders['asks'] = orders['asks'][:limit]
        return orders

    def get_order_book_frame(self, limit=None, kind='auth', pair=None):
        """Get orderbook as a dataframe."""
        q = self.get_order_book(limit, kind, pair)
        asks = pd.DataFrame(q['asks'])
        bids = pd.DataFrame(q['bids'])
        index = pd.MultiIndex.from_product(
            [('asks', 'bids'), ('price', 'volume')])
        df = pd.DataFrame(
            pd.concat([asks, bids], axis=1).values, columns=index)
        return df

    def get_trades(self, limit=None, kind='auth', since=None, pair=None):
        """Get a list of the most recent trades."""
        params = {'pair': self.main.pair if pair is None else pair}
        if since is not None:
            params['since'] = since
        trades = self.main.api_request('trades', params, kind=kind)
        if limit is not None:
            trades['trades'] = trades['trades'][:limit]
        return trades

    def get_trades_frame(self, limit=None, kind='auth', since=None, pair=None):
        """Get a dataframe of the most recent trades."""
        trades = self.get_trades(limit, kind, since, pair)
        df = pd.DataFrame(trades['trades'])
        if not df.empty:
            df.index = pd.to_datetime(df.timestamp, unit='ms')
            df.price = df.price.apply(pd.to_numeric)
            df.volume = df.volume.apply(pd.to_numeric)
            df.drop('timestamp', axis=1, inplace=True)
        else:
            log.warning('Empty response from get_trades. Returning empty df')
        return df
