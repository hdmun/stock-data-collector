import os
import unittest

from protocol.request import InvestorsRequest, TickMarketRequest
from repository import RequestRepository


class RequestRepositoryTest(unittest.TestCase):
    def test_flush_and_load(self):
        # given
        filename = 'request.json'
        tick_requests = [
            TickMarketRequest(path='/tick/market', code='000270', last_date=None),
            TickMarketRequest(path='/tick/market', code='003550', last_date=None),
            TickMarketRequest(path='/tick/market', code='035420', last_date=None)
        ]
        investor_requests = [
            InvestorsRequest(path='/investors', code='101730', last_date=None),
            InvestorsRequest(path='/investors', code='091990', last_date=None),
            InvestorsRequest(path='/investors', code='293490', last_date=None)
        ]
        repository = RequestRepository(filename)
        for request in tick_requests:
            repository.push(request)
        for request in investor_requests:
            repository.push(request)
        repository.flush()

        # when
        repository = RequestRepository(filename)
        repository.load()

        # then
        self.assertFalse(repository.empty)
        self.assertIsNone(repository.message)
        os.remove(filename)

    def test_push_pop(self):
        # given
        filename = 'request.json'
        tick_requests = [
            TickMarketRequest(path='/tick/market', code='000270', last_date=None),
            TickMarketRequest(path='/tick/market', code='003550', last_date=None),
            TickMarketRequest(path='/tick/market', code='035420', last_date=None)
        ]
        repository = RequestRepository(filename)
        for request in tick_requests:
            repository.push(request)

        # when
        message: TickMarketRequest = repository.pop()

        # then
        self.assertIsInstance(message, TickMarketRequest)
        self.assertEqual('/tick/market', message.path)
        self.assertEqual('000270', message.code)
        self.assertIsNone(message.last_date)
