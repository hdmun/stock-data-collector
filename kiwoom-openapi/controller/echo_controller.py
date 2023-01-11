#!/usr/bin/python3
# -*-coding: utf-8 -*-

import asyncio
from datetime import datetime

import zmq
import zmq.asyncio

import protocol
from openapi import KiwoomOpenAPI, ResponseError
from openapi.client import KiwoomOpenAPIClient
from router import Router
from service.push_service import PushService


echo = Router()

class EchoController(object):
    """zmq.REP를 사용해 메세지를 받아 메세지를 처리 후 응답"""

    def __init__(self,
                 zmqctx: zmq.asyncio.Context,
                 push_service: PushService,
                 openapi_client: KiwoomOpenAPIClient):
        self._rep_sock = zmqctx.socket(zmq.REP)
        self._push_service = push_service
        self._openapi_client = openapi_client

    def bind(self, host: str, echo_port: int, push_port: int):
        self._rep_sock.bind(f'{host}:{echo_port}')
        self._push_service.bind(f'{host}:{push_port}')

    async def listen(self):
        while True:
            try:
                message: protocol.RequestMessage = await self._rep_sock.recv_pyobj()
                if not isinstance(message, protocol.RequestMessage):
                    self.reply(error_code=-1, message='invalid message')
                    continue

                asyncio.create_task(echo.process(self, message))
            except Exception as ex:
                self._rep_sock.send_pyobj(ex)
                print(ex)

    def reply(self, error_code: int, message: str):
        self.reply_message(protocol.ResponseMessage(
            error_code=error_code, message=message))

    def reply_message(self, data: protocol.ResponseMessage):
        self._rep_sock.send_pyobj(data)

    @echo.route('/connect')
    async def on_connect_openapi(self, _: protocol.RequestMessage):
        if self._openapi_client.connected:
            self.reply(error_code=0, message='already connect')
            return

        # check connect timeout?
        error_code = self._openapi_client.connect(api=KiwoomOpenAPI())
        if error_code != ResponseError.NONE:
            self.reply(error_code=1, message='failed to connect')
            return

        self.reply(error_code=0, message='connect openapi')

    @echo.route('/disconnect')
    async def on_disconnect_openapi(self, _: protocol.RequestMessage):
        if not self._openapi_client.connected:
            self.reply(error_code=0, message='already disconnected')
            return

        # check connect timeout?
        self._openapi_client.disconnect()
        self.reply(error_code=0, message='disconnect openapi')

    @echo.route('/get/stocks')
    async def on_get_stocks(self, _: protocol.RequestMessage):
        if not self._openapi_client.connected:
            self.reply(error_code=1, message='not connected openapi')
            return

        kospi = self._openapi_client.get_stock_items_by_kospi()
        kosdaq = self._openapi_client.get_stock_items_by_kosdaq()
        futures = self._openapi_client.get_stock_items_by_futures()

        self.reply_message(protocol.GetStocksResponse(
            kospi=kospi, kosdaq=kosdaq, futures=futures))

    @echo.route('/tick/market')
    async def on_get_tick_market(self, request: protocol.TickMarketRequest):
        if not self._openapi_client.connected:
            self.reply(error_code=1, message='not connected openapi')
            return

        result = await self._openapi_client.request_tick_market(
            request.code, last_date=request.last_date)

        self._push_service.push('/tick/market', request.code, result)

        print(f'`/tick/market`. code: {request.code}, count: {len(result)}')

        self.reply(error_code=0, message='succes')

    @echo.route('/investors')
    async def on_get_investors(self, request: protocol.InvestorsRequest):
        if not self._openapi_client.connected:
            self.reply(error_code=1, message='not connected openapi')
            return

        result = await self._openapi_client.request_investors(
            request.code, first_date=datetime.now(), last_date=request.last_date)

        self._push_service.push('/investors', request.code, result)

        print(f'`/investors`. code: {request.code}, count: {len(result)}')

        self.reply(error_code=0, message='succes')
