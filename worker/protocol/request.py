
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class RequestMessage(object):
    path: str


class MarketCode(Enum):
    Kospi = 1
    Kosdaq = 2
    Future = 3


@dataclass(frozen=True)
class TickMarketRequest(RequestMessage):
    code: str
    last_date: datetime


@dataclass(frozen=True)
class InvestorsRequest(RequestMessage):
    code: str
    last_date: datetime


@dataclass(frozen=True)
class PushMessage(RequestMessage):
    path: str
    code: str
    datas: list[list[str]]
