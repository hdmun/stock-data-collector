
import asyncio

import zmq
import zmq.asyncio
from model.openapi import InvestorDataModel, TickDataModel
from protocol import PushMessage
from router import Router


pull = Router()

class PullController(object):
    def __init__(self, zmqctx: zmq.asyncio.Context):
        self._pull_sock = zmqctx.socket(zmq.PULL)

    def connect(self, host: str, port: int):
        self._pull_sock.connect(f'{host}:{port}')

    async def recv_message(self):
        while True:
            try:
                message = await self._pull_sock.recv_pyobj()
                if not isinstance(message, PushMessage):
                    print(f'invalid message type: {type(message)}')
                    continue

                asyncio.create_task(pull.process(self, message))
            except Exception as ex:
                self._pull_sock.send_pyobj(ex)
                print(ex)

    @pull.route('/tick/market')
    async def on_tick_market(self, message: PushMessage):
        # transform
        for tick in message.datas:
            model = TickDataModel(message.code, *tick)

        # validate
        # send to sinker

    @pull.route('/investors')
    async def on_investors(self, message: PushMessage):
        # transform
        for investors in message.datas:
            model = InvestorDataModel(message.code, *investors)

        # validate
        # send to sinker
