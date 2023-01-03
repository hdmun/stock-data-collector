import unittest

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI, Market
from openapi.request.opt10079 import Opt10079, Opt10079Response


@unittest.skip('로그인이 필요하니 수동으로 호출 할 때만 주석 처리하고 테스트 하자.')
class KiwoomOpenAPITests(unittest.IsolatedAsyncioTestCase):
    qtapp: QApplication = QApplication([])
    openapi: KiwoomOpenAPI = KiwoomOpenAPI()

    @classmethod
    def setUpClass(cls):
        cls.openapi = KiwoomOpenAPI()  # given
        guid = cls.openapi.control()  # when
        assert '{a1574a0d-6bfa-4bd7-9020-ded88711818d}' == guid  # then

        def __on_connection(error_code: int):
            if error_code == 0:
                print('connected openapi')
            else:
                print(f'disconnected openapi, error: {error_code}')

            error_code_ = error_code
            login_event_loop.exit()

        error_code_ = 0
        cls.openapi.set_connect_handler(__on_connection)
        cls.openapi.connect()
        login_event_loop = QEventLoop()
        login_event_loop.exec()

        assert error_code_ == 0

    @classmethod
    def tearDownClass(cls):
        cls.qtapp = None
        cls.openapi = None

    def test_get_code_list(self):
        # given
        for market in Market:
            # when
            code_list = self.openapi.get_code_list(market=market)

            # then
            self.assertGreater(len(code_list), 0)

            for code in code_list:
                self.assertIsInstance(code, str)

                name = self.openapi.get_master_code_name(code)
                self.assertNotEqual('', name)
                self.assertIsInstance(name, str)

    async def test_request_tick(self):
        def _on_receive_tr_data(
            screen_no: str,
            req_name: str,
            tran_code: str,
            record_name: str,
            prev_next: str,
            _1: int, _2: str, _3: str, _4: str  # deprecated
        ):
            if not req_name == request_opt.req_name:
                request_opt._exit()
                raise ValueError(f'invalid request name. '
                                 f'request: {request_opt.req_name}, '
                                 f'receive: {req_name}')
            if not tran_code == request_opt.tran_code:
                request_opt._exit()
                raise ValueError(f'invalid request tran_code'
                                 f'request: {request_opt.req_name}, '
                                 f'receive: {req_name}')

            request_opt._set_continue_next(prev_next)
            request_opt.on_receive_tr_data()
            request_opt._exit()

        # given
        code = '005930'
        last_dt = None
        adj_stock_price = 0
        self.openapi.set_trade_data_handler(_on_receive_tr_data)

        # when
        request_opt = Opt10079(self.qtapp, self.openapi)
        response: Opt10079Response = await request_opt.request(code, last_dt, adj_stock_price)

        # then
        self.assertEqual(code, response.code)
        self.assertGreater(len(response.tick_data), 0)

        self.openapi.reset_trade_data_handler()
