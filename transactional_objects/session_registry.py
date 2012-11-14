from .session import Session


__all__ = ['SessionRegistry']


class SessionRegistry(object):
    transaction_storage = None

    def initialize(self, transaction_storage):
        self.transaction_storage = transaction_storage

    def get_session(self):
        assert self.transaction_storage is not None, "SessionRegistry.initialize not called"
        return Session(self.transaction_storage)

    def clean(self):
        "useful for tests"
        self.transaction_storage.clean()
        self.transaction_storage = None


SessionRegistry = SessionRegistry()
