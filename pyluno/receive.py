"""Receive Module."""


class Receive(object):
    """Receive related methods."""

    def __init__(self, main):
        """Initialise with super's main."""
        self.main = main

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
        return self.main.api_request('funding_address', params, kind=kind)

    def create_receive_address(self, asset='XBT'):
        """Create a receive address.

        Allocates a new receive address to your account.
        There is a rate limit of 1 address per hour,
        but bursts of up to 10 addresses are allowed.
        """
        data = {
            'asset': asset,
        }
        result = self.main.api_request('funding_address',
                                       data=data, http_call='post')
        return result
