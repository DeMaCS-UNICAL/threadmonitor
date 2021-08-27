#class LockQueue
#class ConditionQueue


import threading
from threadmonitor.utils import singleton


class Event(list):
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)


class EventHandler:
    def __init__(self) -> None:
        self.events = {}
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def registerEvent(self, key: str, ev: Event) -> Event:
        try:
            self.lock.acquire()
            self.events[key] = ev
            self.condition.notifyAll()
            self.lock.release()
        finally:
            return self.events[key]

    def registerCallback(self, key, callback):
        with self.lock:
            while key not in self.events.keys():
                self.condition.wait()
            self.events[key].append(callback)


@singleton
class ThreadEventHandler(EventHandler):
    pass

class ThreadEvent(Event):
    def __init__(self, key: str):
        ThreadEventHandler().registerEvent(key, self)
    

@singleton
class LockEventHandler(EventHandler):
    pass

class LockEvent(Event):
    def __init__(self, key: str):
        LockEventHandler().registerEvent(key, self)


@singleton
class ConditionEventHandler(EventHandler):
    pass

class ConditionEvent(Event):
    def __init__(self, key: str):
        ConditionEventHandler().registerEvent(key, self)


@singleton
class GeneralEventHandler(EventHandler):
    pass

class GeneralEvent(Event):    
    def __init__(self, key: str):
        GeneralEventHandler().registerEvent(key, self)