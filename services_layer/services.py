from typing import Optional
from datetime import date
from services_layer.unit_of_work import AbstractUnitOfWork
from domain import model


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        orderid: str, sku: str, qty: int,
        uow: AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batches = product.batches
        batchref = model.allocate(line, batches)
    return batchref


def add_batch(
        ref: str, sku: str, qty: int, eta: Optional[date],
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))