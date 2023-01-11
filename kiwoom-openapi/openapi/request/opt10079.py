#!/usr/bin/python3
# -*-coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI
from openapi.request.tran import TrContinueNext, TransactionRequest


class Opt10079(TransactionRequest):
    ticks = [1, 3, 5, 10, 30]

    def __init__(self, qtapp: QApplication, api: KiwoomOpenAPI):
        super().__init__(req_name='주식틱차트조회요청', tran_code = 'OPT10079',
                         api=api, qtapp=qtapp)

        self._req_code = ''
        self._req_tick = ''
        self._req_last_dt = None
        self._result = list[list[str]]()

    async def request(self, code: str, last_dt: datetime=None,
                      adj_stock_price=0, multiple=True) -> list[list[str]]:
        """틱 데이터를 조회합니다.

        데이터 건수를 지정할 수 없고, 데이터 유무에따라 한번에 최대 900개가 조회됩니다.

        Args:
            code - 종목코드
            last_dt - 조회 날짜

        Returns:
            조회된 데이터를 반환
        """

        _TICK = 1  # 틱 범위는 1틱 고정
        self._req_code = code
        self._req_tick = _TICK
        self._req_last_dt = last_dt

        def __set_request_params():
            """요청 전에 필요한 paramter 값을 세팅한다."""
            self._api.set_input_value('종목코드', code)
            self._api.set_input_value('틱범위', f'{_TICK}')
            self._api.set_input_value('수정주가구분', f'{adj_stock_price}')

        __set_request_params()
        await self._request_data(0, '0101')

        while multiple and self._continue_next:
            __set_request_params()
            await self._request_data(2, '0101')

        return self._result

    def on_receive_tr_data(self):
        """수신된 틱 데이터를 처리합니다."""

        for data in self._get_request_data_ex():
            trade_time_str = data[2].strip()  # 체결시간
            trade_datetime = datetime.strptime(trade_time_str, "%Y%m%d%H%M%S")
            if self._req_last_dt and trade_datetime <= self._req_last_dt:
                print(f'request stop market tick. '
                      f'{self._req_code}, {self._req_tick}, '
                      f'{self._req_last_dt}, {trade_time_str}')
                self._set_continue_next(TrContinueNext.Stop)
                break

            self._result.append(data)
        # end of for i in range(count):
