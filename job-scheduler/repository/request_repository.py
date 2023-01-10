#!/usr/bin/python3
# -*-coding: utf-8 -*-

import dataclasses
import json
import os

from protocol.request import RequestMessage


class RequestRepository(object):
    def __init__(self, filename: str):
        self._filename = filename
        self._queue = list[RequestMessage]()
        self._message: RequestMessage = None

    def load(self):
        def __to(item: dict | None) -> RequestMessage | None:
            if item is None:
                return None

            module_name = item.pop('module')
            type_name = item.pop('type')
            class_ = getattr(__import__(module_name), type_name)
            return class_(**item)

        if os.path.exists(self._filename):
            with open(self._filename, 'r') as fp:
                obj = json.load(fp)
                request = obj['request']
                self._queue = list(map(__to, obj['queue']))
                self._message = __to(request) if request else None

    def flush(self):
        def __to(request: RequestMessage) -> dict:
            obj = dataclasses.asdict(request)
            obj['module'] = request.__module__
            obj['type'] = request.__class__.__name__
            return obj

        with open(self._filename, 'w') as fp:
            queue_obj = [__to(request) for request in self._queue]
            request_obj = dataclasses.asdict(self._message) if self._message else None
            json.dump({
                'queue': queue_obj,
                'request': request_obj
            }, fp=fp)

    @property
    def empty(self) -> bool:
        return not len(self._queue)

    def push(self, message: RequestMessage):
        self._queue.append(message)

    def pop(self) -> RequestMessage:
        self._message = self._queue.pop(0)
        return self._message

    @property
    def message(self) -> RequestMessage:
        return self._message
