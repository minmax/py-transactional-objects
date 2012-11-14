from unittest2 import TestCase

from .session_registry import SessionRegistry
from .transaction_storages import SimpleTransactionStorage
from .decorators import pickleable, modifier
from .interface_inspector import InterfaceInspector

from .proxy import ProxyFactory


class ProxyTest(TestCase):
    def test_python_int(self):
        one = 1
        val = self._get_proxy_value(one)
        self.assertTrue(1 == val)
        self.assertEqual(str(val), str(1))
        self.assertTrue(2 > val)

    def _get_proxy_value(self, value):
        class Container(object):
            def __init__(self, value):
                self.value = value

            def get_value(self):
                return self.value
        proxy = self.proxy_factory.get_proxy(Container(value))
        return proxy.get_value()

    def setUp(self):
        class FakeSession(object):
            def changing(self, obj):
                pass
        session = FakeSession()
        self.proxy_factory = ProxyFactory(session)


class InterfaceInspectorTest(TestCase):
    class Testable(object):
        def set_x(self, x):
            pass

        def get_x(self):
            pass

        def _private(self):
            pass

        def public(self):
            pass

    def test_scan(self):
        obj = self.Testable()
        spec = InterfaceInspector().get_spec(obj)
        self.assertEqual(spec.getters, ['get_x'])
        self.assertEqual(spec.setters, ['set_x'])


class BaseTransactionalTestCase(TestCase):
    def setUp(self):
        SessionRegistry.initialize(SimpleTransactionStorage())
        self.session = SessionRegistry.get_session()
        self.session.begin()

    def tearDown(self):
        SessionRegistry.clean()


class FullFunctionalTest(BaseTransactionalTestCase):
    @pickleable(attributes=['value'])
    class ValueStorage(object):
        def __init__(self, initial_value):
            self.value = initial_value

        def set_value(self, value):
            self.value = value

        def get_value(self):
            return self.value

    original_obj_arg = 1
    new_obj_arg = 2

    def rollback_test(self):
        obj = self._create_and_modify_object()
        self.session.rollback()

        self.assertEqual(self.original_obj_arg, obj.get_value())

    def commit_test(self):
        obj = self._create_and_modify_object()
        self.session.commit()

        self.assertEqual(self.new_obj_arg, obj.get_value())

    def _create_and_modify_object(self):
        obj = self.ValueStorage(self.original_obj_arg)
        obj = self.session.add(obj)
        obj.set_value(self.new_obj_arg)
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
