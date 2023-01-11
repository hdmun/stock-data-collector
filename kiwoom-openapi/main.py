#!/usr/bin/python3
# -*-coding: utf-8 -*
import asyncio
import json
import os

import zmq.asyncio
from PyQt5.QtWidgets import QApplication
from model.config import Config

from openapi.client import KiwoomOpenAPIClient
from controller.echo_controller import EchoController
from service.push_service import PushService


def load_config(filename: str) -> Config:
    with open(filename, 'r') as config_fp:
        return Config(**json.load(fp=config_fp))


async def main():
    config = load_config(filename=os.environ['CONFIG_FILENAME'])

    zmqctx = zmq.asyncio.Context()
    openapi_client = KiwoomOpenAPIClient(qtapp=QApplication([]))
    push_service = PushService(zmqctx)
    echo_controller = EchoController(
        zmqctx=zmqctx,
        push_service=push_service,
        openapi_client=openapi_client
    )

    echo_controller.bind(config.host, config.echo_port, config.push_port)
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