
from services_layer.unit_of_work import AbstractUnitOfWork
from domain import model, events
import email


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        event: events.AllocationRequired,
        uow: AbstractUnitOfWork) -> str:
    line = model.OrderLine(event.orderid, event.sku, event.qty)
    with uow:
        product = uow.products.get(line.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        return batchref


def add_batch(
        event: events.BatchCreated,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(event.ref, event.sku, event.qty, event.eta))


def send_out_of_stock_notification(
        event: events.OutofStock,
        uow: AbstractUnitOfWork):
    email.send(
        'stock@made.com',
        f'OutofStock for {event.sku}'
    )


def change_batch_quantity(
        event: events.BatchQuantityChanged,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batchref(batchref = event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
