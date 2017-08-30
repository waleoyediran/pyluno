from __future__ import absolute_import

import json
import logging
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from . import meta
from .ratelimit import RateLimiter

__version__ = meta.__version__

log = logging.getLogger(__name__)

# --------------------------- constants -----------------------


class LunoAPIError(ValueError):
    """Generic Error Class"""
    def __init__(self, response):
        self.url = response.url
        self.code = response.status_code
        self.message = response.text

    def __str__(self):
        return "Luno request %s failed with %d: %s" % (
            self.url, self.code, self.message)


class LunoAPIRateLimitError(ValueError):
    """Generic rate limit error class."""
    def __init__(self, response):
        self.url = response.url
        self.code = response.status_code
        self.message = response.text

    def __str__(self):
        return "Rate Limit Error.\nLuno request %s failed with %d: %s" % (
            self.url, self.code, self.message)


class Luno:
    """Main Luno API class"""
    def __init__(self, key, secret, options={}):
        self.options = options
        self.auth = (key, secret)
        if 'hostname' in options:
            self.hostname = options['hostname']
        else:
            self.hostname = 'api.mybitx.com'
        self.port = options['port'] if 'port' in options else 443
        self.pair = options['pair'] if 'pair' in options else 'XBTZAR'
        self.ca = options['ca'] if 'ca' in options else None
        self.timeout = options['timeout'] if 'timeout' in options else 30
        self.maxRate = options['maxRate'] if 'maxRate' in options else 1
        self.maxBurst = options['maxBurst'] if 'maxBurst' in options else 5
        self.headers = {
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'User-Agent': 'py-luno v' + __version__
        }
        # Use a Requests session so that we can keep headers and connections
        # across API requests
        self._requests_session = requests.Session()
        self._requests_session.headers.update(self.headers)
        self._executor = ThreadPoolExecutor(max_workers=5)

    def close(self):
        """Close connection."""
        log.info('Asking MultiThreadPool to shutdown')
        self._executor.shutdown(wait=True)
        log.info('MultiThreadPool has shutdown')

    def construct_url(self, call):
        """Construc API Url."""
        base = self.hostname
        if self.port != 443:
            base += ':%d' % (self.port,)
        return "https://%s/api/1/%s" % (base, call)

    @RateLimiter
    def api_request(self, call, params, kind='auth', http_call='get'):
        """General API request.

        Generally, use the convenience functions below
        :param kind: the type of request to make. 'auth' makes an
            authenticated call; 'basic' is unauthenticated
        :param call: the API call to make
        :param params: a dict of query parameters
        :return: a json response, a LunoAPIError is thrown if
            the api returns with an error
        """
        url = self.construct_url(call)
        auth = self.auth if kind == 'auth' else None
        if http_call == 'get':
            response = self._requests_session.get(
                url, params=params, auth=auth, timeout=self.timeout)
        elif http_call == 'post':
            response = self._requests_session.post(
                url, data=params, auth=auth, timeout=self.timeout)
        elif http_call == 'put':
            response = self._requests_session.put(
                url+'/'+params, auth=auth, timeout=self.timeout)
        else:
            raise ValueError('Invalid http_call parameter')
        try:
            result = response.json()
        except ValueError:
            result = {'error': 'No JSON content returned'}
        if response.status_code in [429, 503]:
            log.error('Rate Limit Exceeded')
            raise LunoAPIRateLimitError(response)
        elif response.status_code != 200 or 'error' in result:
            raise LunoAPIError(response)
        else:
            return result

    def get_ticker(self, kind='auth', pair=None):
        """Get the latest ticker indicator for a pair."""
        params = {'pair': self.pair if pair is None else pair}
        return self.api_request('ticker', params, kind=kind)

    def get_all_tickers(self, kind='auth'):
        """Get all the latest ticker indicators."""
        return self.api_request('tickers', None, kind=kind)

    def get_order_book(self, limit=None, kind='auth', pair=None):
        """Get a list of bids and asks in the order book."""
        params = {'pair': self.pair if pair is None else pair}
        orders = self.api_request('orderbook', params, kind=kind)
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
        params = {'pair': self.pair if pair is None else pair}
        if since is not None:
            params['since'] = since
        trades = self.api_request('trades', params, kind=kind)
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

    def create_account(self, currency, name, base_account_id, counter_id):
        """Create a new account in the selected currency.

        :param currency: Currency of account
        :param name: Name of account
        :param base_account_id: Id of the base account
        :param counter_id: Id of the counter account
        :return: dict with name. currency and id of new account
        """
        data = {
            'currency': currency,
            'name': name,
            'base_account_id': base_account_id,
            'counter_id': counter_id
        }
        return self.api_request('accounts', params=data, http_call='post')

    def get_balance(self):
        """Get balances of all accounts."""
        return self.api_request('balance', None)

    def get_transactions(self, account_id, min_row=None, max_row=None):
        """Get list of transactions for an account."""
        params = {}
        if min_row is not None:
            params['min_row'] = min_row
        if max_row is not None:
            params['max_row'] = max_row
        return self.api_request(
            'accounts/%s/transactions' % (account_id,), params)

    def get_transactions_frame(self, account_id, min_row=None, max_row=None):
        """Get dataframe of transactions for an account."""
        tx = self.get_transactions(
            account_id, min_row, max_row)['transactions']
        df = pd.DataFrame(tx)
        df.index = pd.to_datetime(df.timestamp, unit='ms')
        df.drop('timestamp', axis=1, inplace=True)
        return df

    def get_pending_transactions(self, account_id):
        """Get a list of pending transactions for an account."""
        return self.api_request('accounts/%s/pending' % (account_id,), None)

    def get_orders(self, state=None, kind='auth', pair=None):
        """Get a list of most recently placed orders.

        You can specify an optional state='PENDING' parameter to
        restrict the results to only open orders. You can also specify the
            market by using the optional pair parameter.
        The list is truncated after 100 items.
        :param kind: typically 'auth' if you want this to return anything
            useful
        :param state: String optional 'COMPLETE', 'PENDING', or None (default)
        :return:
        """
        params = {'pair': self.pair if pair is None else pair}
        if state is not None:
            params['state'] = state
        return self.api_request('listorders', params, kind=kind)

    def get_orders_frame(self, state=None, kind='auth', pair=None):
        """Get a list of most recently placed orders as a dataframe."""
        q = self.get_orders(state, kind, pair)
        tj = json.dumps(q['orders'])
        df = pd.read_json(
            tj, convert_dates=['creation_timestamp', 'expiration_timestamp'])
        df.index = df.creation_timestamp
        return df

    def create_limit_order(self, order_type, volume, price):
        """Create a new limit order.

        :param order_type: 'buy' or 'sell'
        :param volume: the volume, in BTC
        :param price: the ZAR price per bitcoin
        :return: the order id
        """
        data = {
            'pair': self.pair,
            'type': 'BID' if order_type == 'buy' else 'ASK',
            'volume': str(volume),
            'price': str(price)

        }
        result = self.api_request('postorder', params=data, http_call='post')
        return result

    def create_market_order(self, order_type, volume, base_account_id,
                            counter_account_id):
        """Create a new market order.

        :param order_type: 'buy' or 'sell'
        :param volume: the volume of btc if sell, or currency if buy.
        :return: the order id
        """
        data = {
            'pair': self.pair,
            'type': 'BUY' if order_type == 'buy' else 'SELL',
            'volume': str(volume),
        }
        if order_type is 'buy':
            data['couter_volume'] = volume
        else:
            data['base_volume'] = volume
        result = self.api_request('marketorder', params=data, http_call='post')
        return result

    def stop_order(self, order_id):
        """Stop a specific order.

        :param order_id: The order ID
        :return: a success flag
        """
        data = {
            'order_id': order_id,
        }
        return self.api_request('stoporder', params=data, http_call='post')

    def stop_all_orders(self):
        """Stop all pending orders, both sell and buy.

        :return: dict of Boolean -- whether request succeeded or not for each
            order_id that was pending
        """
        pending = self.get_orders('PENDING')['orders']
        ids = [order['order_id'] for order in pending]
        result = {}
        for order_id in ids:
            status = self.stop_order(order_id)
            result[order_id] = status['success']
        return result

    def get_order(self, order_id):
        """Get an order by its ID.

        :param order_id: string	The order ID
        :return: dict order details or LunoAPIError raised
        """
        return self.api_request('orders/%s' % (order_id,), None)

    def list_trades(self, limit=None, since=None, pair=None):
        """Get list of all trades."""
        params = {'pair': self.pair if pair is None else pair}
        if since is not None:
            params['since'] = since
        trades = self.api_request('listtrades', params)
        if limit is not None:
            trades['trades'] = trades['trades'][:limit]
        return trades

    def list_trades_frame(self, limit=None, since=None, pair=None):
        """Get dataframe of all trades."""
        trades = self.list_trades(limit, since, pair)
        df = pd.DataFrame(trades['trades'])
        if not df.empty:
            df.index = pd.to_datetime(df.timestamp, unit='ms')
            df.price = df.price.apply(pd.to_numeric)
            df.volume = df.volume.apply(pd.to_numeric)
            df.base = df.base.apply(pd.to_numeric)
            df.counter = df.counter.apply(pd.to_numeric)
            df.fee_base = df.fee_base.apply(pd.to_numeric)
            df.drop('timestamp', axis=1, inplace=True)
        else:
            log.warning('Empty response from list_trades. Returning empty df')
        return df

    def get_fee_info(self, kind='auth', pair=None):
        """Get the fee info for the account."""
        params = {'pair': self.pair if pair is None else pair}
        return self.api_request('fee_info', params, kind=kind)

    def get_receive_address(self, asset, address=None, kind='auth'):
        """Get receive address for the account.

        Returns the default receive address associated with your account
        and the amount received via the address. You can specify an
        optional address parameter to return information for a
        non-default receive address. In the response, total_received
        is the total confirmed Bitcoin amount received excluding
        unconfirmed transactions. total_unconfirmed is the total
        sum of unconfirmed receive transactions.
        """
        params = {'asset': asset,
                  'address': address}
        return self.api_request('funding_address', params, kind=kind)

    def create_receive_address(self, asset='XBT'):
        """Create a receive address.

        Allocates a new receive address to your account.
        There is a rate limit of 1 address per hour,
        but bursts of up to 10 addresses are allowed.
        """
        data = {
            'asset': asset,
        }
        result = self.api_request('funding_address',
                                  params=data, http_call='post')
        return result

    def list_withdrawal_requests(self):
        """Get list of withdrawal requests."""
        trades = self.api_request('withdrawals')
        return trades

    def create_withdrawal_request(self, wtype, amount, beneficiary_id=None):
        """Create a new withdrawal request."""
        data = {
            'type': wtype,
            'amount': amount,
            'beneficiary_id': beneficiary_id,
        }
        result = self.api_request('withdrawals',
                                  params=data, http_call='post')
        return result

    def get_withdrawals_status(self, wid=None):
        """Get status od specific withdrawal.

        :param wid: String.
        :return:
        """
        data = {'id': wid}
        return self.api_request('withdrawals', params=data)

    def delete_withdrawal_request(self, wid):
        """Delete a new withdrawal request."""
        data = {'id': wid}
        result = self.api_request('withdrawals',
                                  params=data, http_call='delete')
        return result

    def send_bitcoin(self, amount, currency, address,
                     description=None, message=None):
        """Send currency to account."""
        data = {
            'amount': amount,
            'currency': currency,
            'address': address,
            'description': description,
            'message': message,
        }
        result = self.api_request('send', params=data, http_call='post')
        return result


    def transfer(self, amount, currency, note,
                 source_account_id, target_account_id):
        """Transfer currency between accounts."""
        data = {
            'amount': amount,
            'currency': currency,
            'note': note,
            'source_account_id': source_account_id,
            'target_account_id': target_account_id,
        }
        result_req = self.api_request('transfers', params=data, http_call='post')
        tx_id = result_req['id']
        data = tx_id
        result_app = self.api_request('transfers', params=data, http_call='put')
        return [result_req, result_app]
