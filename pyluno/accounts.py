"""Accounts Module."""
import json

import pandas as pd


class Account(object):
    """Class with the account methods."""

    def __init__(self, main):
        """Initialise with super's main."""
        self.main = main

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
        return self.main.api_request('accounts', data=data, http_call='post')

    def get_balance(self):
        """Get balances of all accounts."""
        return self.main.api_request('balance', None)

    def get_transactions(self, account_id, min_row=None, max_row=None):
        """Get list of transactions for an account."""
        params = {}
        if min_row is not None:
            params['min_row'] = min_row
        if max_row is not None:
            params['max_row'] = max_row
        return self.main.api_request(
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
        return self.main.api_request(
            'accounts/%s/pending' % (account_id,), None)

    def get_orders(self, state=None, pair=None):
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
        params = {'pair': self.main.pair if pair is None else pair}
        if state is not None:
            params['state'] = state
        return self.main.api_request('listorders', params)

    def get_orders_frame(self, state=None, kind='auth', pair=None):
        """Get a list of most recently placed orders as a dataframe."""
        q = self.get_orders(state, kind, pair)
        tj = json.dumps(q['orders'])
        df = pd.read_json(
            tj, convert_dates=['creation_timestamp', 'expiration_timestamp'])
        df.index = df.creation_timestamp
        return df

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
        result_req = self.main.api_request('transfers', data=data,
                                           http_call='post')
        tx_id = result_req['id']
        data = tx_id
        result_app = self.main.api_request('transfers', data=data,
                                           http_call='put')
        return [result_req, result_app]
