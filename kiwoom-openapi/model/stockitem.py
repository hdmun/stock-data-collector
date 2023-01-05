
from dataclasses import dataclass


@dataclass(frozen=True)
class StockItem(object):
    code: str
    name: str
