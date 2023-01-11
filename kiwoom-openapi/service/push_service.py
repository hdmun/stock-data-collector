
import asyncio

import zmq
import zmq.asyncio

from protocol import PushMessage


class PushService(object):
    def __init__(self, zmqctx: zmq.asyncio.Context):
        self._push_sock = zmqctx.socket(zmq.PUSH)
        self._queue = asyncio.Queue()

    def bind(self, addr: str):
        self._push_sock.bind(addr)

    def push(self, path: str, code: str, data: object):
        self._queue.put_nowait(PushMessage(path, code, data))

    async def start(self):
        while True:
            if self._queue.empty():
                await asyncio.sleep(0.1)
                continue

            message = await self._queue.get()
            await self._push_sock.send_pyobj(message)
