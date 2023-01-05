#!/usr/bin/python3
# -*-coding: utf-8 -*-

import asyncio

import zmq
import zmq.asyncio
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

    @echo.route('/connect')
    async def on_connect_openapi(self):
        # try connect
        # timeout check
        # reply
        pass

    @echo.route('/get/stocks')
    def on_get_stocks(self):
        # request openapi
        # reply
        pass

    @echo.route('/tick/market')
    def on_get_tick_market(self):
        # request openapi
        # push
        # reply
        pass

    @echo.route('/investors')
    def on_get_investors(self):
        # request openapi
        # push
        # reply
        pass
