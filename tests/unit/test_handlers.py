from datetime import date

from services_layer import handlers, messagebus, unit_of_work

from domain import model, events, commands


class TestAddBatch:

    def test_for_new_product(self):
        uow = unit_of_work.InMemoryUnitOfWork()
        messagebus.handle(
            commands.CreateBatch("b1", "CRUNCHY-ARMCHAIR", 100, None),
            uow
        )
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None


class TestAllocate:

    def test_returns_allocation(self):
        uow = unit_of_work.InMemoryUnitOfWork()
        messagebus.handle(commands.CreateBatch("batch1", "COMPLICATED-LAMP", 100, None),uow)
        result = messagebus.handle(commands.Allocate("o1", "COMPLICATED-LAMP", 10), uow)
        assert result[0] == "batch1"

class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = unit_of_work.InMemoryUnitOfWork()
        messagebus.handle(
            commands.CreateBatch("batch1", "ADORABLE-SETTEE", 100, None), uow
        )
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100

        messagebus.handle(commands.ChangeBatchQuantity("batch1", 50), uow)

        assert batch.available_quantity == 50

    def test_reallocates_if_necessary(self):
        uow = unit_of_work.InMemoryUnitOfWork()
        event_history = [
            commands.CreateBatch("batch1", "INDIFFERENT-TABLE", 50, None),
            commands.CreateBatch("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            commands.Allocate("order1", "INDIFFERENT-TABLE", 20),
            commands.Allocate("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history:
            messagebus.handle(e, uow)
        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        messagebus.handle(commands.ChangeBatchQuantity("batch1", 25), uow)

        # order1 or order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
