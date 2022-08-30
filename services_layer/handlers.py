
from services_layer.unit_of_work import AbstractUnitOfWork
from domain import model, events, commands
import email
from adapters import redis_eventpublisher


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
        command: commands.Allocate,
        uow: AbstractUnitOfWork) -> str:
    line = model.OrderLine(command.orderid, command.sku, command.qty)
    with uow:
        product = uow.products.get(line.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batchref = product.allocate(line)
        return batchref


def add_batch(
        command: commands.CreateBatch,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get(sku=command.sku)
        if product is None:
            product = model.Product(command.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(command.ref, command.sku, command.qty, command.eta))


def send_out_of_stock_notification(
        event: events.OutofStock,
        uow: AbstractUnitOfWork):
    email.send(
        'stock@made.com',
        f'OutofStock for {event.sku}'
    )


def change_batch_quantity(
        command: commands.ChangeBatchQuantity,
        uow: AbstractUnitOfWork):
    with uow:
        product = uow.products.get_by_batchref(batchref = command.ref)
        product.change_batch_quantity(ref=command.ref, qty=command.qty)


def publish_allocated_event(event: events.Allocated, uow:AbstractUnitOfWork):
    redis_eventpublisher.publish('line_allocated', event)