#!/usr/bin/python3
# -*-coding: utf-8 -*-

import zmq.asyncio

from protocol.request import RequestMessage
from protocol.response import ResponseMessage


class KiwoomOpenAPIJob(object):
    """kiwoom openapi의 작업을 컨트롤하는 역할 담당

    zeromq.REQ 소켓으로 요청을 보내 정의된 동작을 하도록 한다.
    """

    def __init__(self, zmqctx: zmq.asyncio.Context):
        self._req_sock: zmq.asyncio.Socket = zmqctx.socket(zmq.REQ)

    def connect(self, host: str, port: int):
        self._req_sock.connect(f'{host}:{port}')

    async def request(self, path: str):
        self._req_sock.send_pyobj(RequestMessage(path=path))
        return await self._req_sock.recv_pyobj()

    async def request_message(self, message: RequestMessage):
        self._req_sock.send_pyobj(message)
        return await self._req_sock.recv_pyobj()

    async def run(self):
        connect_response: ResponseMessage = await self.request('/connect')
