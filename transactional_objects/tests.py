from unittest2 import TestCase

from .session_registry import SessionRegistry
from .transaction_storages import SimpleTransactionStorage
from .decorators import pickleable, modifier


class BaseTransactionalTestCase(TestCase):
    def setUp(self):
        SessionRegistry.initialize(SimpleTransactionStorage())
        self.session = SessionRegistry.get_session()
        self.session.begin()

    def tearDown(self):
        SessionRegistry.clean()


@pickleable
class AutoConfigured(object):
    __slots__ = ['obj', 'list']

    def __init__(self, obj, list):
        self.obj = obj
        self.list = list

    @modifier
    def set_obj(self, obj):
        self.obj = obj

    @modifier
    def append(self, value):
        self.list.append(value)


class FullFunctionalTest(BaseTransactionalTestCase):
    original_obj_arg = 1
    new_obj_arg = 2

    def rollback_test(self):
        obj = self._create_and_modify_object()
        self.session.rollback()

        self.assertEqual([1, 2], obj.list)
        self.assertEqual(self.original_obj_arg, obj.obj)

    def commit_test(self):
        obj = self._create_and_modify_object()
        self.session.commit()

        self.assertEqual([1, 2, 3], obj.list)
        self.assertEqual(self.new_obj_arg, obj.obj)

    def _create_and_modify_object(self):
        obj = AutoConfigured(self.original_obj_arg, [1, 2])
        obj.append(3)
        obj.set_obj(self.new_obj_arg)
        return obj


class RecursiveStateTest(BaseTransactionalTestCase):
    @pickleable
    class Root(object):
        __slots__ = ['child']

        def __init__(self, child):
            self.child = child

        @modifier
        def set_child(self, new_child):
            self.child = new_child

    @pickleable
    class Child(object):
        __slots__ = ['name']

        def __init__(self, name):
            self.name = name

        @modifier
        def set_name(self, new_name):
            self.name = new_name

    def runTest(self):
        origin_child = self.Child('origin')
        root = self.Root(origin_child)

        origin_child.set_name('new')

        other_child = self.Child('other')

        root.set_child(other_child)

        self.session.rollback()

        self.assertEquals(origin_child.name, 'origin')
        self.assertIs(origin_child, root.child)
