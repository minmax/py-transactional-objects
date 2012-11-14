class Spec(object):
    def __init__(self, getters, setters):
        self.getters = getters
        self.setters = setters


class InterfaceInspector(object):
    @staticmethod
    def is_public_method_name(name):
        return not name.startswith('_')

    def get_spec(self, obj):
        public_methods_names = self._get_public_methods_names(obj)
        return Spec(
            self._get_getters_names(public_methods_names),
            self._get_setters_names(public_methods_names)
        )

    def _get_public_methods_names(self, obj):
        return filter(self.is_public_method_name, dir(obj))

    def _get_getters_names(self, names):
        return filter(self._is_getter_name, names)

    def _is_getter_name(self, name):
        return name.startswith('get_') or name.startswith('is_')

    def _get_setters_names(self, names):
        return filter(self._is_setter_name, names)

    def _is_setter_name(self, name):
        return name.startswith('set_')
