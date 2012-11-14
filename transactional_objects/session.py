from .transaction import Transaction
from .errors import TransactionNotDefined


__all__ = ['Session']


class Session(object):
    def __init__(self, transaction_storage):
        self.transaction_storage = transaction_storage

    def commit(self):
        self._init_new_transaction()

    def begin(self):
        self._init_new_transaction()

    def rollback(self):
        try:
            self.transaction.rollback()
        finally:
            self._init_new_transaction()

    def changing(self, obj):
        self.transaction.changing(obj)

    @property
    def transaction(self):
        try:
            return self.transaction_storage.get_transaction()
        except TransactionNotDefined:
            return self._init_new_transaction()

    def _init_new_transaction(self):
        transaction = Transaction()
        self.transaction_storage.set_transaction(transaction)
        return transaction

    def clean(self):
        self.transaction_storage.clean()
