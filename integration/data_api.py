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

    def get_by_dates(self, dates, snapshots=None):
        """
        Get data for all branches in the list of dates provided. Use snapshot data if provided.

        :param dates: list of dates to query
        :param snapshots: dict of snapshot data
        :return: dict of data keyed by branch
        """
        transactions = {}

        for branch, branch_id in self.branches.items():
            branch_snapshot = snapshots.get(branch) if isinstance(snapshots, dict) else None
            transactions[branch] = self.get_by_dates_branch(dates, branch_id, branch_snapshot=branch_snapshot)

        return transactions

    def get_by_dates_branch(self, dates, branch_id, branch_snapshot=None, retrieve_historical=False):
        """
        Providing a branch_snapshot allows us to override making a call to the API.

        :param dates: the dates we wish to get data for
        :param branch_id: the id of the branch we want data for
        :param branch_snapshot: dict of the format {date: {data}}
        :param retrieve_historical: do not attempt to get data from a before a snapshot
        :return: dict of data keyed by date
        """
        if isinstance(branch_snapshot, dict):
            transactions = {date: data for date, data in branch_snapshot.items() if date in dates}
        else:
            transactions = {}

        for date in dates:
            if not retrieve_historical and transactions:
                if max(transactions) >= date:
                    continue

            if date not in transactions:
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
