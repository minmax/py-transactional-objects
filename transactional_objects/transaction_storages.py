from threading import local

from .errors import TransactionNotDefined


__all__ = [
    'ThreadLocalTransactionStorage',
    'SimpleTransactionStorage',
]


class ThreadLocalTransactionStorage(object):
    def __init__(self):
        self._local = local()

    def get_transaction(self):
        try:
            return self._local.transaction
        except AttributeError:
            raise TransactionNotDefined()

    def set_transaction(self, transaction):
        self._local.transaction = transaction

    def clean(self):
        self._local = local()


class SimpleTransactionStorage(object):
    def get_transaction(self):
        try:
            return self._transaction
        except AttributeError:
            raise TransactionNotDefined()

    def set_transaction(self, transaction):
        self._transaction = transaction

    def clean(self):
        del self._transaction
