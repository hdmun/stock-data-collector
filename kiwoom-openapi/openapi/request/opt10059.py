#!/usr/bin/python3
# -*-coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI
from openapi.request.tran import TrContinueNext, TransactionRequest


@dataclass(frozen=True)
class InvestorData(object):
    date: str
    value: str  #  현재가
    ratio: str  #  전일대비
    rate: str  #  등락율
    accumulate_volume: str  #  누적거래량
    accumulate_value: str  #  누적거래대금
    personal: str  #  개인투자자
    foreigner: str  #  외국인투자자
    company: str  #  기관계
    financial_investor: str  #  금융투자
    insurance: str  #  보험
    investor_trust: str  #  투신
    etc_financial: str  #  기타금융
    bank: str  #  은행
    pension_fund: str  #  연기금등
    private_fund: str  #  사모펀드
    country: str  #  국가
    other_corp: str  #  기타법인
    fake_foreigner: str  #  내외국


@dataclass(frozen=True)
class Opt10059Response(object):
    code: str
    data: list[InvestorData]


class Opt10059(TransactionRequest):
    def __init__(self, qtapp: QApplication, api: KiwoomOpenAPI):
        super().__init__(req_name='종목별투자자기관별요청',
                         tran_code = 'OPT10059',
                         api=api, qtapp=qtapp)

        self._req_code = ''
        self._req_last_date = None
        self._investor_data = list[InvestorData]()

    async def request(self, code: str, first_date: datetime,
                      last_date: datetime=None, multiple=True) -> Opt10059Response:
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

        return Opt10059Response(code=code, data=self._investor_data)

    def on_receive_tr_data(self):
        last_dt = self._req_last_date

        count = self._api.get_receive_count(self.tran_code, self.req_name)
        for i in range(count):
            date_str = self._get_request_data('일자', index=i).strip()
            date = datetime.strptime(date_str, "%Y%m%d")
            if last_dt and date < last_dt:
                print(f'request stop market investors.'
                      f'{self._req_code}, {last_dt}, {date}')
                self._set_continue_next(TrContinueNext.Stop)
                break

            data = InvestorData(
                date=date.strftime('%Y-%m-%d'),
                value= self._get_request_data('현재가', index=i),
                ratio=self._get_request_data('전일대비', index=i),
                rate=self._get_request_data('등락율', index=i),
                accumulate_volume=self._get_request_data('누적거래량', index=i),
                accumulate_value=self._get_request_data('누적거래대금', index=i),
                personal=self._get_request_data('개인투자자', index=i),
                foreigner=self._get_request_data('외국인투자자', index=i),
                company=self._get_request_data('기관계', index=i),
                financial_investor=self._get_request_data('금융투자', index=i),
                insurance=self._get_request_data('보험', index=i),
                investor_trust=self._get_request_data('투신', index=i),
                etc_financial=self._get_request_data('기타금융', index=i),
                bank=self._get_request_data('은행', index=i),
                pension_fund=self._get_request_data('연기금등', index=i),
                private_fund=self._get_request_data('사모펀드', index=i),
                country=self._get_request_data('국가', index=i),
                other_corp=self._get_request_data('기타법인', index=i),
                fake_foreigner=self._get_request_data('내외국인', index=i),
            )
            self._investor_data.append(data)
        # for i in range(count):
