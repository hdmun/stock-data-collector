#!/usr/bin/python3
# -*-coding: utf-8 -*
import asyncio

import zmq.asyncio
from PyQt5.QtWidgets import QApplication

from openapi.client import KiwoomOpenAPIClient
from controller.echo_controller import EchoController
from service.push_service import PushService


async def main():
    zmqctx = zmq.asyncio.Context()
    openapi_client = KiwoomOpenAPIClient(qtapp=QApplication([]))
    push_service = PushService(zmqctx)
    echo_controller = EchoController(
        zmqctx=zmqctx,
        push_service=push_service,
        openapi_client=openapi_client
    )

    echo_controller.bind(host='tcp://127.0.0.1', echo_port=7070, push_port=7071)
    await asyncio.gather(
        echo_controller.listen(),
        push_service.start()
    )


if __name__ == '__main__':
    try:
        print('running kiwoom opeapi')
        asyncio.run(main())
    except Exception as ex:
        print(ex)
        raise ex