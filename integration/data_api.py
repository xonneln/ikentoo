"""
Works with:

https://integration.ikentoo.com/integration/1/transactions

TODO expand to all API endpoints.

"""

import logging
import time

import requests


class IkentooData(object):

    def __init__(self, url, user_name, password, attempts=10, branches=None):
        self.url = url
        self.user_name = user_name
        self.password = password
        self.attempts = attempts
        self.branches = branches

    def get_by_dates(self, dates):
        return {branch: self.get_by_dates_branch(dates, branch_id) for branch, branch_id in self.branches.items()}

    def get_by_dates_branch(self, dates, branch_id):
        transactions = {}

        for date in dates:
            date_str = '{:%Y-%m-%d}'.format(date)
            params = {'businessLocationId': branch_id,
                      'startDate': date_str,
                      'endDate': date_str}

            # Dirty hack
            for attempt in range(self.attempts):
                auth = requests.auth.HTTPBasicAuth(self.user_name, self.password)
                response = requests.get(self.url, auth=auth, params=params)
                if response.status_code == 200:
                    break
                else:
                    logging.info('status_code={0}'.format(response.status_code))
                    time.sleep(10)

            transactions[date] = response.json()

        return transactions
