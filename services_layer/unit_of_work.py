import abc
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import config

from adapters import repository
from services_layer import messagebus


class AbstractUnitOfWork(abc.ABC):
    '''
    Implements context manager. If execution is normal I chose to commit full unit of work
    If exceptions then some type of roll back
    What commit and roll back mean is left to the specific implementation'''
    
    products: repository.AbstractProductRepository # the UoW binds to a 'companion' repository

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback(exc_type, exc_val)

    def commit(self):
        self._commit() # this gets implemented only in the real classes
        self.publish_events()

    def publish_events(self):
        for product in self.products.seen:
            while product.events:
                event = product.events.pop(0)
                messagebus.handle(event)

    @abc.abstractmethod
    def rollback(self, exc_type, exc_val):
        raise NotImplementedError


class InMemoryUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.products = repository.InMemoryProductRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self, exc_type, exc_val):
        print(f'Unit of work no executed because {exc_type} with {exc_val}')


DEFAULT_FACTORY = sessionmaker().configure(bind=config.get_inmemory_uri())

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory = DEFAULT_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.products = repository.SqlAlchemyProductRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self, exc_type, exc_val):
        self.session.rollback()
        print(f'Unit of work no executed because {exc_type} with {exc_val}')




