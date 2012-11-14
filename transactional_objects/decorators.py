from functools import wraps

from .session_registry import SessionRegistry
from .errors import TransactionalObjectsConfigureError


__all__ = [
    'pickleable',
    'modifier',
]


def pickleable(cls=None, attributes=None):
    assert not isinstance(attributes, basestring)

    def decorator(cls):
        if attributes is None:
            if not getattr(cls, '__slots__', None):
                raise TransactionalObjectsConfigureError('Class %s must provide __slots__' % cls)
            attributes_list = cls.__slots__
        else:
            attributes_list = attributes

        if not _is_method_defined_in_current_cls(cls, '__getstate__'):
            def __getstate__(self):
                return dict(
                    (name, getattr(self, name)) for name in attributes_list
                )
            cls.__getstate__ = __getstate__

        if not _is_method_defined_in_current_cls(cls, '__setstate__'):
            def __setstate__(self, state):
                for name, value in state.iteritems():
                    setattr(self, name, value)
            cls.__setstate__ = __setstate__
        return cls
    return decorator(cls) if cls is not None else decorator


def _is_method_defined_in_current_cls(cls, method_name):
    try:
        original_method = getattr(cls, method_name)
    except AttributeError:
        return False

    for base_cls in cls.mro()[1:]:
        try:
            base_method = getattr(base_cls, method_name)
        except AttributeError:
            return False
        else:
            if original_method == base_method:
                return False
    return True


def modifier(method):
    @wraps(method)
    def wrapper(obj, *args, **kwargs):
        session = SessionRegistry.get_session()
        session.changing(obj)
        return method(obj, *args, **kwargs)
    return wrapper
