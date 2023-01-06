import unittest

from model import StockItem
from openapi import KiwoomOpenAPI, Market
from openapi.client import KiwoomOpenAPIClient


class KiwoomOpenAPIMock(KiwoomOpenAPI):
    def get_code_list(self, market: Market) -> list[str]:
        if market == Market.KOSPI:
            return ['000080', '000150', '000270', '207940', '210780']
        return ['263750', '293490', '112040', '253450', '035760']

    def get_future_code_list(self) -> list[str]:
        return ['101T3000', '105T1000', '105T2000', '106T3000', '1A3T3000']

    def get_master_code_name(self, code: str) -> str:
        return {
            '000080': '하이트진로',
            '000150': '두산',
            '000270': '기아',
            '207940': '삼성바이오로직스',
            '210780': 'TIGER 코스피고배당',
            '263750': '펄어비스',
            '293490': '카카오게임즈',
            '112040': '위메이드',
            '253450': '스튜디오드래곤',
            '035760': 'CJ ENM',
            '101T3000': 'F 202303',
            '105T1000': '미니 F 202301',
            '105T2000': '미니 F 202302',
            '106T3000': '코스닥 F 202303',
            '1A3T3000': '경기소비재 F202303',
        }[code]



class KiwoomOpenAPIClientTests(unittest.IsolatedAsyncioTestCase):
    def test_connect(self):
        pass  # todo

    def test_get_stocks(self):
        # given
        api_mock = KiwoomOpenAPIMock()
        client = KiwoomOpenAPIClient(api=api_mock)

        # when
        kospi = client.get_stock_items_by_kospi()
        kosdaq = client.get_stock_items_by_kosdaq()
        futures = client.get_stock_items_by_futures()

        def __to_stockitem(code: str):
            return StockItem(code, api_mock.get_master_code_name(code))

        # then
        self.assertListEqual(list(
            map(__to_stockitem, api_mock.get_code_list(Market.KOSPI))
        ), kospi)

        self.assertListEqual(list(
            map(__to_stockitem, api_mock.get_code_list(Market.KOSDAQ))
        ), kosdaq)

        self.assertListEqual(list(
            map(__to_stockitem, api_mock.get_future_code_list())
        ), futures)
