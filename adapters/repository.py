import abc
from typing import Any, Set
from domain import model
from domain.model import Product
from adapters import orm


class AbstractProductRepository(abc.ABC):
    """
    Repository exists at the aggregate level, in this case Product
    """

    def __init__(self):
        self.seen: Set[model.Product] = set()

    def add(self, product: Product):
        """
        Add to repository
        """
        self._add(product)
        self.seen.add(product)

    def get(self, sku: str) -> Product:
        """
        Get from repository
        """
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    def get_by_batchref(self, batchref) -> model.Product:
        product = self._get_by_batchref(batchref)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_batchref(self, batchref) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self, *args) -> None:
        """
        Make changes permanent in repository
        """
        raise NotImplementedError


class InMemoryProductRepository(AbstractProductRepository):
    """
    One of the main advantages of the repository pattern is that it allows to write
    'fake repositories that make testing very easy, as well to write easy to understand MVPs
    The Product Repository holds products and each product has its batches
    """

    def __init__(self,
                 products=None) -> None:
        super().__init__()
        if products:
            self._products = set(products)
        else:
            self._products = set()
        self.committed = False  # No impact of real in memory implications but useful for testing

    def _add(self, item):
        if isinstance(item, Product):
            self._products.add(item)
        else:
            raise Exception("Trying to add something that is not a Product")

    def _get(self, sku) -> model.Product:
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref) -> model.Product:
        return next((
            p for p in self._products for b in p.batches if b.reference == batchref), None)

    def commit(self, *args):
        self.committed = True  # No impact of real in memory implications but useful for testing

    def list(self):
        return list(self._products)

class SqlAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, product):
        self.session.add(product)

    def _get(self, sku) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).first()

    def _get_by_batchref(self, batchref) -> model.Product:
        return self.session.query(model.Product).join(model.Batch)\
                    .filter(orm.batches.c.reference == batchref,).first()

    def list(self):
        return self.session.query(model.Product).all()

    def commit(self, *args) -> None:
        self.session.commit()