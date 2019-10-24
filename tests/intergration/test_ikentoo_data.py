import datetime
from unittest import TestCase

import mock
import requests

import integration.data_api
import tests.intergration.test_data


class TestIkentooData(TestCase):

    def setUp(self):
        self.url = 'https://integration.ikentoo.com/integration/1/transactions'
        self.user_name = 'a.goldman@birdcage.com'
        self.password = 'password'
        self.attempts = 10
        self.branches = {'Miami Beach': '123'}

        self.ikentoo = integration.data_api.IkentooData(self.url,
                                                        self.user_name,
                                                        self.password,
                                                        attempts=self.attempts,
                                                        branches=self.branches)

        self.json = tests.intergration.test_data.TRANS_DATA

    @mock.patch('integration.data_api.requests', autospec=True)
    def test_get_by_dates(self, mock_requests):
        mock_response = mock.Mock(spec=requests.models.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = self.json

        mock_requests.get.return_value = mock_response

        date = datetime.date(2019, 1, 1)

        transactions = self.ikentoo.get_by_dates([date])

        for branch in self.branches.keys():
            self.assertEqual(transactions[branch][date], self.json)
