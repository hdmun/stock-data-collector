import unittest

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI, Market


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
