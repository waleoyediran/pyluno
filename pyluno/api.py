"""Base API Module."""
from __future__ import absolute_import

import logging
from concurrent.futures import ThreadPoolExecutor

import requests

from . import meta
from .accounts import Account
from .market import Market
from .orders import Orders
from .quotes import Quotes
from .receive import Receive
from .utils import LunoAPIError, LunoAPIRateLimitError, RateLimiter, deprecated
from .withdrawal import withdrawal

__version__ = meta.__version__

log = logging.getLogger(__name__)


class Luno(object):
    """Main Luno API class."""

    def __init__(self, key, secret, options={}):
        """Instantiate with key and secret if authentication is wanted."""
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
        self.maxRate = options['maxRate'] if 'maxRate' in options else 0.1
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

        self.account = Account(self)
        self.market = Market(self)
        self.orders = Orders(self)
        self.quotes = Quotes(self)
        self.receive = Receive(self)
        self.withdrawal = withdrawal(self)

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
    def api_request(self, call, params=None, data=None,
                    kind='auth', http_call='get'):
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
        response = self._requests_session.request(
            http_call.upper(),
            url, params=params, data=data, auth=auth, timeout=self.timeout)
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

    # @deprecated('Use account.create_account instead')
    # def create_account(self, *args, **kwargs):
    #     return self.account.create_account(args, kwargs)
    #
    # @deprecated('Use account.get_balance instead')
    # def get_balance(self):
    #     return self.account.get_balance()
    #
    # @deprecated('Use account.get_transactions instead')
    # def get_transactions(self, *args, **kwargs):
    #     return self.account.get_transactions(args, kwargs)
    #
    # @deprecated('Use account.get_transactions_frame instead')
    # def get_transactions_frame(self, *args, **kwargs):
    #     return self.account.get_transactions_frame(args, kwargs)
    #
    # @deprecated('Use account.get_pending_transactions instead')
    # def get_pending_transactions(self, *args, **kwargs):
    #     return self.account.get_pending_transactions(args, kwargs)
    #
    # @deprecated('Use account.get_orders instead')
    # def get_orders(self, *args, **kwargs):
    #     return self.account.get_orders(args, kwargs)
    #
    # @deprecated('Use account.get_orders instead')
    # def get_orders(self, *args, **kwargs):
    #     return self.account.get_orders(args, kwargs)
