import email
from typing import Union, List
from domain import events, commands
from services_layer.handlers import *
import logging
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential

Message = Union[commands.Command, events.Event]

logger = logging.getLogger(__name__)

def handle(
        message: Message,
        uow: AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            command_result = handle_command(message, queue, uow)
            results.append(command_result)
        else:
            raise Exception(f'{message} was not Event nor Command')
    return results


def handle_event(
        event: events.Event,
        queue: List[Message],
        uow: AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential()
            ):
                with attempt:
                    logger.debug('handling event %s with handler %s', event, handler)
                    handler(event, uow=uow)
                    queue.extend(uow.collect_new_messages())
        except RetryError as retry_failure:
            logger.error('Failed to handle event %s times, giving up!', retry_failure.last_attempt.attempt_number)
            continue


def handle_command(
        command: commands.Command,
        queue: List[Message],
        uow: AbstractUnitOfWork):
    logger.debug('jandling command %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_messages())
        return result
    except Exception:
        logger.exception('Exception handling command %s', command)
        raise

EVENT_HANDLERS = {
    events.OutofStock: [send_out_of_stock_notification],
    events.Allocated: [publish_allocated_event]
}

COMMAND_HANDLERS = {
    commands.Allocate: allocate,
    commands.CreateBatch: add_batch,
    commands.ChangeBatchQuantity: change_batch_quantity
} # type Dict[Type[commands.Command], Callable]