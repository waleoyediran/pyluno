"""Quotes module."""


class Quotes(object):
    """Class for quote related methods."""

    def __init__(self, main):
        """Initialise with super's main."""
        self.main = main

    def get_quote(self, ttype, base_amount, pair):
        """Get temporary quote."""
        data = {
            'type': ttype,
            'base_amount': base_amount,
            'pair': pair,
        }
        result = self.main.api_request('quotes', data=data, http_call='post')
        return result

    def get_quote_status(self, wid):
        """Get status of a specific quote."""
        data = {'id': wid}
        result = self.main.api_request('quotes',
                                       params=data)
        return result

    def execute_quote(self, wid):
        """Execute trade based on quote."""
        data = {'id': wid}
        result = self.main.api_request('quotes', params=data, http_call='put')
        return result

    def delete_quote(self, wid):
        """Delete quote."""
        data = {'id': wid}
        result = self.main.api_request('quotes', params=data,
                                       http_call='delete')
        return result
