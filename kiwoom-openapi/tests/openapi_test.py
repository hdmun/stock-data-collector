import unittest

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI

class KiwoomOpenAPITests(unittest.IsolatedAsyncioTestCase):
    qtapp: QApplication = None

    def setUp(self):
        self.qtapp = QApplication([])

    def tearDown(self):
        self.qtapp = None

    def test_initialize(self):
        # given
        openapi = KiwoomOpenAPI()
        # when
        guid = openapi.control()
        # then
        self.assertEqual('{a1574a0d-6bfa-4bd7-9020-ded88711818d}', guid)

    @unittest.skip('OpenAPI 모듈 유닛 테스트 방법에 대해 고민 좀 해보자')
    def test_login(self):
        def _on_connection(error_code: int):
            if error_code == 0:
                print('connected openapi')
            else:
                print(f'disconnected openapi, error: {error_code}')

            login_event_loop.exit()

        openapi = KiwoomOpenAPI()
        openapi.set_connect_handler(_on_connection)

        openapi.connect()
        login_event_loop = QEventLoop()
        login_event_loop.exec()
