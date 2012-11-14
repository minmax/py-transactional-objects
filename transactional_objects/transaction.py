from copy import copy


__all__ = ['Transaction']


class RollbackRecord(object):
    def __init__(self, obj, state):
        self.obj = obj
        self.state = state

    def rollback(self):
        self.obj.__setstate__(self.state)


class Transaction(object):
    def __init__(self):
        self.clean()

    def rollback(self):
        for rollback_record in self.dirty_objects:
            rollback_record.rollback()
        self.clean()

    def clean(self):
        self.dirty_object_ids = set()
        self.dirty_objects = []

    def changing(self, obj):
        if self._is_dirty(obj):
            return
        self._mark_as_changed_and_save_state(obj)

    def _mark_as_changed_and_save_state(self, obj):
        self.dirty_object_ids.add(id(obj))
        state = obj.__getstate__()
        state = self._convert_state(state)
        self.dirty_objects.append(RollbackRecord(obj, state))

    def _convert_state(self, state):
        new_state = {}
        for attr_name, obj in state.iteritems():
            if not self._is_dirty(obj):
                obj = copy(obj)
            new_state[attr_name] = obj
        return new_state

    def _is_dirty(self, obj):
        return id(obj) in self.dirty_object_ids
