#!/usr/bin/python3
# -*-coding: utf-8 -*-

import dataclasses
import json
import os

from model.stockitem import StockItem


class StockItemRepository(object):
    def __init__(self, filename: str):
        self._filename = filename
        self._kospi = list[StockItem]()
        self._kosdaq = list[StockItem]()
        self._future = list[StockItem]()

    def load(self):
        def __to(item: dict) -> StockItem:
            return StockItem(**item)

        if os.path.exists(self._filename):
            with open(self._filename, 'r') as fp:
                obj = json.load(fp)
                self._kospi = list(map(__to, obj['kospi']))
                self._kosdaq = list(map(__to, obj['kosdaq']))
                self._future = list(map(__to, obj['future']))

    def flush(self):
        with open(self._filename, 'w') as fp:
            json.dump({
                'kospi': [dataclasses.asdict(item) for item in self.kospi],
                'kosdaq': [dataclasses.asdict(item) for item in self.kosdaq],
                'future': [dataclasses.asdict(item) for item in self.future]
            }, fp=fp, ensure_ascii=True)  # 직접 수정할게 아니니 유니코드로 쓰자

    def update(self, kospi: list[StockItem], kosdaq: list[StockItem],
               future: list[StockItem]):
        self._kospi = kospi
        self._kosdaq = kosdaq
        self._future = future

    @property
    def kospi(self) -> list[StockItem]:
        return self._kospi

    @property
    def kosdaq(self) -> list[StockItem]:
        return self._kosdaq

    @property
    def future(self) -> list[StockItem]:
        return self._future
