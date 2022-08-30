from dataclasses import dataclass
from typing import Optional
from datetime import date

class Event:
    pass

@dataclass
class OutofStock(Event):
    sku: str

@dataclass
class BatchCreated(Event):
    ref: str
    sku: str
    qty: int
    eta: Optional[date] = None

@dataclass
class Allocated(Event):
    orderid: str
    sku: str
    qty: int
    batchref: str

@dataclass
class BatchQuantityChanged(Event):
    ref: str
    qty: int
