from interfaces.events import EventBus as EventBusInterface
from botocore.hooks import HierarchicalEmitter, EventAliaser


class EventBus(EventAliaser, EventBusInterface):
    def __init__(self):
        super(EventBus, self).__init__(HierarchicalEmitter())
