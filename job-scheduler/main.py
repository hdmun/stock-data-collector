#!/usr/bin/python3
# -*-coding: utf-8 -*
import asyncio
import json

import zmq.asyncio

from jobs.kiwoom_openapi import KiwoomOpenAPIJob
from model.config import JobConfig
from repository import RequestRepository, StockItemRepository


def load_job_config(filename: str) -> JobConfig:
    with open(filename, 'r') as config_fp:
        config_json = json.load(fp=config_fp)

    kiwoom_addr = config_json['kiwoom_addr']
    return JobConfig(kiwoom_addr=(kiwoom_addr['host'], kiwoom_addr['port']))


async def main():
    try:
        job_config = load_job_config(filename='job_config.json')
    except FileNotFoundError as ex:
        print('setup to config file')
        raise ex

    zmqctx = zmq.asyncio.Context()
    job = KiwoomOpenAPIJob(
        zmqctx=zmqctx,
        request_repository=RequestRepository(filename='request.json'),
        stock_item_repository=StockItemRepository(filename='stock_items.json')
    )

    host, port = job_config.kiwoom_addr
    job.connect(host, port)
    await job.setup()
    await job.run()


if __name__ == '__main__':
    try:
        print('running job scheduler')

        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as ex:
        print(ex)
        raise ex
