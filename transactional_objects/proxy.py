from itertools import chain, izip, repeat

from functools import update_wrapper

from .interface_inspector import InterfaceInspector


class ProxyFactory(object):
    inspector = InterfaceInspector()

    def __init__(self, session):
        self.session = session

    def get_proxy(self, original):
        proxy = Proxy(original)
        spec = self.inspector.get_spec(original)

        decorators = chain(
            izip(spec.getters, repeat(Getter)),
            izip(spec.setters, repeat(Setter)),
        )

        for name, factory in decorators:
            method = getattr(original, name)
            wrapper = factory(self, original, method)
            setattr(proxy, name, wrapper)

        return proxy


class MethodWrapper(object):
    @classmethod
    def create(cls, proxy_factory, obj, method):
        wrapper = cls(proxy_factory, obj, method)
        update_wrapper(wrapper, method)
        return wrapper

    def __init__(self, proxy_factory, obj, method):
        self.proxy_factory = proxy_factory
        self.obj = obj
        self.method = method

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class Getter(MethodWrapper):
    base_types = frozenset([int, long, bool, str, unicode, tuple, frozenset])

    def __call__(self, *args, **kwargs):
        result = self.method(*args, **kwargs)
        if self._is_python_object(result):
            return result
        else:
            return self.proxy_factory.get_proxy(result)

    def _is_python_object(self, obj):
        return type(obj) in self.base_types


class Setter(MethodWrapper):
    def __call__(self, *args, **kwargs):
        self.proxy_factory.session.changing(self.obj)
        self.method(*args, **kwargs)


class Proxy(object):
    def __init__(self, original):
        self.__original = original

    def __getattr__(self, name):
        if not InterfaceInspector.is_public_method_name(name):
            return getattr(self.__original, name)
        else:
            return object.__dict__[name]

    def __eq__(self, other):
        return other == self.__original
