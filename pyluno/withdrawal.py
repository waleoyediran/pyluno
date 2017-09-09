"""withdrawal Module."""


class withdrawal(object):
    """withdrawal methods."""

    def __init__(self, main):
        """Initialise with super's main."""
        self.main = main

    def list_withdrawal_requests(self):
        """Get list of withdrawal requests."""
        trades = self.main.api_request('withdrawals')
        return trades

    def create_withdrawal_request(self, wtype, amount, beneficiary_id=None):
        """Create a new withdrawal request."""
        data = {
            'type': wtype,
            'amount': amount,
            'beneficiary_id': beneficiary_id,
        }
        result = self.main.api_request('withdrawals',
                                       data=data, http_call='post')
        return result

    def get_withdrawals_status(self, wid=None):
        """Get status od specific withdrawal.

        :param wid: String.
        :return:
        """
        data = {'id': wid}
        return self.main.api_request('withdrawals', params=data)

    def delete_withdrawal_request(self, wid):
        """Delete a new withdrawal request."""
        data = {'id': wid}
        result = self.main.api_request('withdrawals',
                                       params=data, http_call='delete')
        return result
