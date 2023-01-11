#!/usr/bin/python3
# -*-coding: utf-8 -*-

import asyncio
import time
from enum import StrEnum

from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI, ResponseError


REQ_SLEEP = 3.7
TRAN_TIMEOUT = 3600


class TrContinueNext(StrEnum):
    Stop = '0'
    Continue = '2'


class TransactionRequest(object):
    def __init__(self, req_name: str, tran_code: str, qtapp: QApplication,
                 api: KiwoomOpenAPI, wait_time=REQ_SLEEP):
        self._req_name = req_name
        self._tran_code = tran_code

        self._qtapp = qtapp
        self._api = api
        self._wait_time = wait_time
        self._wait = False

        self._tran_prev_next = ''

    def __repr__(self) -> str:
        return f'(req_name={self.req_name}, tran_code={self.tran_code})'

    @property
    def req_name(self) -> str:
        return self._req_name

    @property
    def tran_code(self) -> str:
        return self._tran_code

    def on_receive_tr_data(self):
        raise NotImplementedError(f'implement on_receive_tr_data')

    async def _request_data(self, prev_next: int, screen_no: str):
        error = self._api.request_data(
            self.req_name, self.tran_code, prev_next, screen_no)
        if error != ResponseError.NONE:
            print(f'error in api.request_data. error: {error}')

            while error == ResponseError.SISE_OVERFLOW:
                await asyncio.sleep(self._wait_time * 1.5)

                error = self._api.request_data(
                    self.req_name, self.tran_code, prev_next, screen_no)
                print(f'request _request_data in while. error: {error}')

        await self._wait_qteventloop()

    async def _wait_qteventloop(self):
        time_s = time.time()
        self._wait = True
        while self._wait:
            wait_time = time.time() - time_s
            if wait_time >= TRAN_TIMEOUT:
                error_message = (f'TransactionRequest wait time to long. '
                                 f'wait_time: {wait_time}')
                print(f'{error_message} {repr(self)}')
                raise TimeoutError(error_message)

            if self._qtapp.hasPendingEvents():
                self._qtapp.processEvents()
                time_s = time.time()
            await asyncio.sleep(0)

        await asyncio.sleep(self._wait_time)  # 1시간당 1,000건 제한 때문에 대기

    def _exit(self):
        self._wait = False

    @property
    def _continue_next(self) -> bool:
        return self._tran_prev_next == TrContinueNext.Continue

    def _set_continue_next(self, value: TrContinueNext):
        self._tran_prev_next = value

    def _get_request_data(self, field_name: str, index:int) -> str:
        data = self._api.get_request_data(
            self.tran_code, '', index, field_name)
        if not data:
            return data

        operator_prefix = data[:2]
        if operator_prefix == '+-':  # 이런 케이스가 있었는지 생각이 안 난다.
            data = data[2:]  # slice
            print(f'comm_get_data convert +-. '
                  f'{self.req_name}, {self.tran_code}, {field_name}, {data}')

        return data

    def _get_request_data_ex(self) -> list[list[str]]:
        return self._api.get_request_data_ex(self.tran_code, '')
