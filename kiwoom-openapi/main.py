#!/usr/bin/python3
# -*-coding: utf-8 -*
import asyncio

from PyQt5.QtWidgets import QApplication

from openapi import KiwoomOpenAPI
from openapi.client import KiwoomOpenAPIClient


async def main():
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