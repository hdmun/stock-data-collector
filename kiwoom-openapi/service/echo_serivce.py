#!/usr/bin/python3
# -*-coding: utf-8 -*-

import asyncio

import zmq
import zmq.asyncio

import protocol
from openapi import ResponseError
from openapi.client import KiwoomOpenAPIClient
from router import Router


echo = Router()

class EchoService(object):
    """zmq.REP를 사용해 메세지를 받아 메세지를 처리 후 응답"""

    def __init__(self, zmqctx: zmq.asyncio.Context, port: int,
                 openapi_client: KiwoomOpenAPIClient):
        self._rep_sock = zmqctx.socket(zmq.REP)
        self._rep_sock.bind(f'tcp://172.30.1.50:{port}')
        self._openapi_client = openapi_client

    async def recv_message(self):
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
        error_code = self._openapi_client.connect()
        if error_code != ResponseError.NONE:
            self.reply(error_code=1, message='failed to connect')
            return

        self.reply(error_code=0, message='connect openapi')

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
    def on_get_tick_market(self, request: protocol.TickMarketRequest):
        # request openapi
        # push
        # reply
        pass

    @echo.route('/investors')
    def on_get_investors(self, request: protocol.InvestorsRequest):
        # request openapi
        # push
        # reply
        pass
