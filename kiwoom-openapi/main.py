#!/usr/bin/python3
# -*-coding: utf-8 -*
import asyncio

import zmq.asyncio
from PyQt5.QtWidgets import QApplication

from openapi.client import KiwoomOpenAPIClient
from service.echo_serivce import EchoService


async def main():
    zmqctx = zmq.asyncio.Context()
    openapi_client = KiwoomOpenAPIClient(qtapp=QApplication([]))
    echo_service = EchoService(
        zmqctx, port=7070, openapi_client=openapi_client)

    await echo_service.recv_message()

if __name__ == '__main__':
    try:
        print('running kiwoom opeapi')
        asyncio.run(main())
    except Exception as ex:
        print(ex)
        raise ex