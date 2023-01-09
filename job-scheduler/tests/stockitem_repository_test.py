import os
import unittest

from model.stockitem import StockItem
from repository.stockitem_repository import StockItemRepository


class StockItemRepositoryTest(unittest.TestCase):
    def test_flush_and_load(self):
        # given
        filename = 'stock_items_test.json'

        kospi_data = [
            StockItem(code='000270', name='기아'),
            StockItem(code='003550', name='LG'),
            StockItem(code='035420', name='NAVER')
        ]
        kosdaq_data = [
            StockItem(code='101730', name='위메이드맥스'),
            StockItem(code='091990', name='셀트리온헬스케어'),
            StockItem(code='293490', name='카카오게임즈')
        ]
        future_data = [
            StockItem(code='101T3000', name='F 202303'),
            StockItem(code='101T3000', name='F 202303'),
            StockItem(code='101T3000', name='F 202303')
        ]

        # when
        repository = StockItemRepository(filename)
        repository.kospi.extend(kospi_data)
        repository.kosdaq.extend(kosdaq_data)
        repository.future.extend(future_data)
        repository.flush()

        repository = StockItemRepository(filename)
        repository.load()
        os.remove(filename)

        # then
        self.assertListEqual(kospi_data, repository.kospi)
        self.assertListEqual(kosdaq_data, repository.kosdaq)
        self.assertListEqual(future_data, repository.future)
