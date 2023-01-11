#!/usr/bin/python3
# -*-coding: utf-8 -*-

from datetime import datetime

from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication

from model import StockItem
from openapi import KiwoomOpenAPI, Market, ResponseError
from openapi.request import Opt10059, Opt10079
from openapi.request.tran import TransactionRequest


ERROR_CONNECT_USER = -100 # 사용자 정보교환 실패
ERROR_CONNECT_SERVER = -101 # 서버접속 실패
ERROR_CONNECT_VERSION = -102 # 버전처리 실패


class KiwoomOpenAPIClient(object):
    """'KiwoomOpenAPI' 클래스를 사용해 요청을 담당하는 클래스"""

    def __init__(self, qtapp: QApplication):
        self._qtapp = qtapp
        self._api: KiwoomOpenAPI = None
        self._login_event_loop: QEventLoop = None
        self._error_code: ResponseError = ResponseError.NONE
        self._request: TransactionRequest = None

    @property
    def connected(self) -> bool:
        return self._api.connected if self._api else False

    def connect(self, api: KiwoomOpenAPI) -> ResponseError:
        if self._api and self._api.connected:
            raise Exception('duplicate connect KiwoomOpenAPI')

        self._api = api
        self._api.set_connect_handler(self._on_connect_event)
        self._api.set_trade_data_handler(self._on_receive_tr_data)
        print('initialize KiwoomOpenAPI')

        self._api.connect()
        self._login_event_loop = QEventLoop()
        self._login_event_loop.exec_()
        return self._error_code

    def disconnect(self):
        if not self._api:
            return

        self._api.clear()
        print('disconnect KiwoomOpenAPI')

    def _on_connect_event(self, error_code: int):
        if error_code == 0:
            print('connected KiwoomOpenAPI')
        else:
            print(f'disconnected KiwoomOpenAPI|{error_code}')

        self._error_code = error_code
        self._login_event_loop.exit()

    def get_stock_items_by_kospi(self) -> list[StockItem]:
        return list(map(
            lambda code: StockItem(code, self._api.get_master_code_name(code)),
            self._api.get_code_list(Market.KOSPI)
        ))

    def get_stock_items_by_kosdaq(self) -> list[StockItem]:
        return list(map(
            lambda code: StockItem(code, self._api.get_master_code_name(code)),
            self._api.get_code_list(Market.KOSDAQ)
        ))

    def get_stock_items_by_futures(self) -> list[StockItem]:
        return list(map(
            lambda code: StockItem(code, self._api.get_master_code_name(code)),
            self._api.get_future_code_list()
        ))

    def _on_receive_tr_data(self, screen_no: str, req_name: str, tran_code: str,
                            record_name: str, prev_next: str,
                            _1: int, _2: str, _3: str, _4: str  # deprecated
        ):
            try:
                assert req_name == self._request.req_name
                assert tran_code == self._request.tran_code

                self._request._set_continue_next(prev_next)
                self._request.on_receive_tr_data()
            except Exception as ex:
                raise ex
            finally:
                self._request._exit()

    async def request_tick_market(self, code: str, last_date: datetime) -> list[list[str]]:
        if self._request is not None:
            # duplicate request
            return

        self._request = Opt10079(qtapp=self._qtapp, api=self._api)
        response = await self._request.request(code, last_date)
        self._request = None
        return response

    async def request_investors(self, code: str, first_date: datetime,
                                last_date: datetime) -> list[list[str]]:
        if self._request is not None:
            # duplicate request
            return

        self._request = Opt10059(qtapp=self._qtapp, api=self._api)
        response = await self._request.request(code, first_date, last_date)
        self._request = None
        return response
