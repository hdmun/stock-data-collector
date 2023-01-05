#!/usr/bin/python3
# -*-coding: utf-8 -*-

class Router(object):
    def __init__(self):
        self._handler = dict[str, callable]()

    def route(self, path: str):
        def decorator(func: callable):
            if path in self._handler:
                raise ValueError(f"duplicate path '{path}'")

            self._handler[path] = func
            return func
        return decorator

    async def process(self, path: str, self_, args):
        if path not in self._handler:
            raise ValueError(f"invalid path '{path}'")

        await self._handler[path](self_, args)
