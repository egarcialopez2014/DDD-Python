from datetime import date, timedelta
from domain.model import Batch, OrderLine, allocate

tomorrow = date.today() + timedelta(days=1)

def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta = None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta = tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta = None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta = tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference