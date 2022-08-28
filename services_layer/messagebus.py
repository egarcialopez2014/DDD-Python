import email

from domain import events
from services_layer.handlers import *


def handle(
        event: events.Event,
        uow: AbstractUnitOfWork):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results



HANDLERS = {
    events.OutofStock: [send_out_of_stock_notification],
    events.AllocationRequired: [allocate],
    events.BatchCreated: [add_batch],
    events.BatchQuantityChanged: [change_batch_quantity]
}