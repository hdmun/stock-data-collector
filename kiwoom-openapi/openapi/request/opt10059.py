#!/usr/bin/python3
# -*-coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI
from openapi.request.tran import TrContinueNext, TransactionRequest


class Opt10059(TransactionRequest):
    def __init__(self, qtapp: QApplication, api: KiwoomOpenAPI):
        super().__init__(req_name='종목별투자자기관별요청',
                         tran_code = 'OPT10059',
                         api=api, qtapp=qtapp)

        self._req_code = ''
        self._req_last_date = None
        self._result = list[list[str]]()

    async def request(self, code: str, first_date: datetime,
                      last_date: datetime=None, multiple=True) -> list[list[str]]:
        """특정 종목의 투자자, 기관들의 거래 정보를 조회합니다."""

        self._req_code = code
        self._req_last_date = last_date

        def __set_request_params():
            """요청 전에 필요한 paramter 값을 세팅한다."""
            self._api.set_input_value('일자', first_date.strftime('%Y%m%d'))
            self._api.set_input_value('종목코드', code)
            self._api.set_input_value('금액수량구분', '2')  # 1:금액, 2:수량
            self._api.set_input_value('매매구분', '0')  # 0:순매수, 1:매수, 2:매도
            self._api.set_input_value('단위구분', '1')  # 1000:천주, 1:단주

        __set_request_params()
        await self._request_data(0, '0101')

        while multiple and self._continue_next:
            __set_request_params()
            await self._request_data(2, '0101')

        return self._result

    def on_receive_tr_data(self):
        last_dt = self._req_last_date

        for data in self._get_request_data_ex():
            date_str = data[0].strip()
            date = datetime.strptime(date_str, "%Y%m%d")
            if last_dt and date < last_dt:
                print(f'request stop market investors.'
                      f'{self._req_code}, {last_dt}, {date}')
                self._set_continue_next(TrContinueNext.Stop)
                break

            self._result.append(data)
        # for data in self._get_request_data_ex():
