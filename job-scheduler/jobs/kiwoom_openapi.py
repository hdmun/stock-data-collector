#!/usr/bin/python3
# -*-coding: utf-8 -*-

import zmq.asyncio
from model.stockitem import StockItem

from protocol.request import RequestMessage, TickMarketRequest, InvestorsRequest
from protocol.response import (
    ResponseMessage,
    GetStocksResponse
)
from repository import RequestRepository, StockItemRepository


class KiwoomOpenAPIJob(object):
    """kiwoom openapi의 작업을 컨트롤하는 역할 담당

    zeromq.REQ 소켓으로 요청을 보내 정의된 동작을 하도록 한다.
    """

    def __init__(self, zmqctx: zmq.asyncio.Context,
                 request_repository: RequestRepository,
                 stock_item_repository: StockItemRepository):
        self._req_sock: zmq.asyncio.Socket = zmqctx.socket(zmq.REQ)
        self._request_repository = request_repository
        self._stock_item_repository = stock_item_repository

    def connect(self, host: str, port: int):
        self._req_sock.connect(f'{host}:{port}')

    async def request(self, path: str):
        self._req_sock.send_pyobj(RequestMessage(path=path))
        return await self._req_sock.recv_pyobj()

    async def request_message(self, message: RequestMessage) -> ResponseMessage:
        self._req_sock.send_pyobj(message)
        return await self._req_sock.recv_pyobj()

    async def setup(self):
        self._request_repository.load()
        self._stock_item_repository.load()

        # check maintenence
        # check connection state

        connection: ResponseMessage = await self.request('/connect')
        if connection.error_code != 0:
            # todo: error
            return

        # 종목 코드 업데이트
        stock_items: GetStocksResponse = await self.request('/get/stocks')
        if stock_items.error_code != 0:
            # todo: error
            return

        print(f'`/get/stocks`, kospi: {len(stock_items.kospi)}, '
              f'kosdaq: {len(stock_items.kosdaq)}, '
              f'future: {len(stock_items.futures)}')

        self._update_stock_items(stock_items.futures, stock_items.kosdaq,
                                 stock_items.kospi)

        # 요청 데이터 큐가 비어있으면 채워주자
        if self._request_repository.empty:
            # todo: meger list kospi, kosdaq

            for stock in stock_items.kospi:
                self._request_repository.push(InvestorsRequest(
                    path='/investors',
                    code=stock.code,
                    last_date=None
                ))
                self._request_repository.push(TickMarketRequest(
                    path='/tick/market',
                    code=stock.code,
                    last_date=None
                ))
            for stock in stock_items.kosdaq:
                self._request_repository.push(InvestorsRequest(
                    path='/investors',
                    code=stock.code,
                    last_date=None
                ))
                self._request_repository.push(TickMarketRequest(
                    path='/tick/market',
                    code=stock.code,
                    last_date=None
                ))
            # todo: future tick request

    async def run(self):
        while not self._request_repository.empty:
            # todo: check maintenence

            message = self._request_repository.message
            if message is None:
                message = self._request_repository.pop()

            response = await self.request_message(message)
            print(f'response error code: {response.error_code}, '
                  f'{response.message}')

            if response.error_code:
                break

            message = self._request_repository.pop()

    def _update_stock_items(self, future: list[StockItem],
                            kosdaq: list[StockItem], kospi: list[StockItem]):
        """종목 정보를 `StockItemRepository`에 업데이트 합니다.
        """

        def __to_dict(stock_items: list[StockItem]) -> dict:
            return {stock.code: stock.name for stock in stock_items}

        def __diff_code_set(from_repo: dict, from_api: dict) -> list[str]:
            return set(from_repo.keys()) - set(from_api.keys())

        def _log_changed_code_list(repo: list[StockItem],
                                   api: list[StockItem]):
            from_repo = __to_dict(repo)
            from_api = __to_dict(api)
            # 상장 폐지
            for code in __diff_code_set(from_repo, from_api):
                print(f'delisting {code}, {from_repo[code]}')
            # 신규 상장
            for code in __diff_code_set(from_api, from_repo): 
                print(f'listing {code}, {from_api[code]}')

        # 변경점 체크 후 로깅
        _log_changed_code_list(self._stock_item_repository.future, future)
        _log_changed_code_list(self._stock_item_repository.kosdaq, kosdaq)
        _log_changed_code_list(self._stock_item_repository.kospi, kospi)

        # API로 부터 받아온 정보로 덮어씌우자
        self._stock_item_repository.update(kospi, kosdaq, future)
        self._stock_item_repository.flush()
