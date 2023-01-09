
from dataclasses import dataclass, field

from model import StockItem


@dataclass(frozen=True)
class ResponseMessage(object):
    error_code: int = 0
    message: str = ''


@dataclass(frozen=True)
class GetStocksResponse(ResponseMessage):
    kospi: list[StockItem] = field(default_factory=list)
    kosdaq: list[StockItem] = field(default_factory=list)
    futures: list[StockItem] = field(default_factory=list)
