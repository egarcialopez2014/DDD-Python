import email

from domain import events


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)

def send_out_of_stock_notification(event: events.OutofStock):
    email.send_mail(
        'stock@made.com',
        f'OutofStock for {event.sku}'
    )

HANDLERS = {
    events.OutofStock: [send_out_of_stock_notification],
}