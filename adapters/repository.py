import abc
from typing import Any
from domain import model
from domain.model import Product


class AbstractProductRepository(abc.ABC):
    """
    Repository exists at the aggregate level, in this case Product
    """

    @abc.abstractmethod
    def add(self, product: Product):
        """
        Add to repository
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku: str) -> Product:
        """
        Get from repository
        """
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
        if products:
            self._products = set(products)
        else:
            self._products = set()
        self.committed = False  # No impact of real in memory implications but useful for testing

    def add(self, item):
        if isinstance(item, Product):
            self._products.add(item)
        else:
            raise Exception("Trying to add something that is not a Product")

    def get(self, sku) -> model.Product:
        return next((p for p in self._products if p.sku == sku), None)


    def commit(self, *args):
        self.committed = True  # No impact of real in memory implications but useful for testing

    def list(self):
        return list(self._products)


class SqlAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product):
        self.session.add(product)

    def get(self, sku) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).one()

    def list(self):
        return self.session.query(model.Product).all()

    def commit(self, *args) -> None:
        self.session.commit()