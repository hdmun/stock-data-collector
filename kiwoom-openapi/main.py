#!/usr/bin/python3
# -*-coding: utf-8 -*
import asyncio

import zmq.asyncio
from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI
from openapi.client import KiwoomOpenAPIClient
from service.echo_serivce import EchoService


async def main():
    zmqctx = zmq.asyncio.Context()
    echo_service = EchoService(zmqctx, port=7070)

    req_manager = KiwoomOpenAPIClient(api=KiwoomOpenAPI())
    await req_manager.connect()


if __name__ == '__main__':
    qtapp = QApplication([])

    try:
        print('running kiwoom opeapi')
        asyncio.run(main())
    except Exception as ex:
        print(ex)
        raise ex