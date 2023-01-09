#!/usr/bin/python3
# -*-coding: utf-8 -*-

from dataclasses import dataclass


@dataclass(frozen=True)
class StockItem(object):
    code: str
    name: str
