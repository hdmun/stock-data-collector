import asyncio
import json

import zmq
import zmq.asyncio
from controller.pull_controller import PullController

from model.config import WorkerConfig


def load_job_config(filename: str) -> WorkerConfig:
    with open(filename, 'r') as config_fp:
        config_json = json.load(fp=config_fp)

    kiwoom_addr = config_json['kiwoom_addr']
    return WorkerConfig(kiwoom_addr=(kiwoom_addr['host'], kiwoom_addr['port']))


async def main():
    try:
        worker_config = load_job_config(filename='worker_config.json')
    except FileNotFoundError as ex:
        print('setup to config file')
        raise ex

    zmqctx = zmq.asyncio.Context()
    pull_controller = PullController(zmqctx)

    host, port = worker_config.kiwoom_addr
    pull_controller.connect(host, port)

    await pull_controller.recv_message()


if __name__ == '__main__':
    try:
        print('running worker')

        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as ex:
        print(ex)
        raise ex
