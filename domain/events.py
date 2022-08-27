from dataclasses import dataclass

class Event:
    pass

@dataclass
class OutofStock(Event):
    sku: str

