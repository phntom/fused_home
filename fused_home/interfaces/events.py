from abc import ABC, abstractmethod


class EventBus(ABC):
    @abstractmethod
    def emit(self, event_name, **kwargs):
        return NotImplemented

    @abstractmethod
    def emit_until_response(self, event_name, **kwargs):
        return NotImplemented

    @abstractmethod
    def register(self, event_name, handler, unique_id=None, unique_id_uses_count=False):
        return NotImplemented

    @abstractmethod
    def register_first(self, event_name, handler, unique_id=None, unique_id_uses_count=False):
        return NotImplemented

    @abstractmethod
    def register_last(self, event_name, handler, unique_id, unique_id_uses_count=False):
        return NotImplemented

    @abstractmethod
    def unregister(self, event_name, handler=None, unique_id=None, unique_id_uses_count=False):
        return NotImplemented
