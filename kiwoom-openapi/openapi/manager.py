#!/usr/bin/python3
# -*-coding: utf-8 -*-

from PyQt5.QtCore import QEventLoop

from openapi import KiwoomOpenAPI


ERROR_CONNECT_USER = -100 # 사용자 정보교환 실패
ERROR_CONNECT_SERVER = -101 # 서버접속 실패
ERROR_CONNECT_VERSION = -102 # 버전처리 실패


class RequestManager(object):
    """'KiwoomOpenAPI' 클래스를 사용해 요청을 담당하는 클래스"""
    def __init__(self, api: KiwoomOpenAPI):
        self._api: KiwoomOpenAPI = api
        self._login_event_loop: QEventLoop = None
        self._error_code = 0

    async def connect(self) -> int:
        if not self._api:
            raise Exception('invalid KiwoomOpenAPI')

        self._api.set_connect_handler(self._on_connect_event)
        print('initialize KiwoomOpenAPI')

        self._api.connect()
        self._login_event_loop = QEventLoop()
        self._login_event_loop.exec_()
        return self._error_code

    def _on_connect_event(self, error_code: int):
        if error_code == 0:
            print('connected KiwoomOpenAPI')
        else:
            print(f'disconnected KiwoomOpenAPI|{error_code}')

        self._error_code = error_code
        self._login_event_loop.exit()
