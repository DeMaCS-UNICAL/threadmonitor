import threading
import copy
from typing import Any
from threadmonitor.utils import singleton


class _Topic(list):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        with self.lock:
            #print(f'callbacks being executed: {self}')
            ret = [f(*args, **kwargs) for f in self]
            #print(f'returning results of call: {ret}')
            return ret

    def __repr__(self):
        return "Topic(%s)" % list.__repr__(self)


class Broker:
    def __init__(self, topicType: _Topic) -> None:
        self.topics = {}
        self.lock = threading.Lock()
        self.callbackCondition = threading.Condition(self.lock)
        self.topicType = topicType

    def _register(self, key: str):
        with self.lock:
            if key not in self.topics.keys():
                #print(f'{self} registering topic {key}')
                self.topics[key] = self.topicType()

    def registerTopic(self, key: str):
        self._register(key)
            
    def registerCallback(self, key, callback, register = True):
        if register and key not in self.topics.keys():
            self._register(key)
        with self.lock:
            self.topics[key].append(callback)
            #print(f'{self} registered callback to {key}')
            self.callbackCondition.notifyAll()

    def sendAndReceive(self, key: str, register = True, *args, **kwargs) -> list:
        if register and key not in self.topics.keys():
            self._register(key)
        if key in self.topics.keys():
            topic = self.topics[key]
            with self.lock:
                while not topic:
                    #print(f'{self} acquired topic, waiting for callbacks to be registered')
                    self.callbackCondition.wait()
            #print(f'{self} topic ready, executing call to topic {key}')
            return copy.deepcopy( topic(*args, **kwargs) )
        return []

    def send(self, key: str, register = True, *args, **kwargs) -> None:
        if register and key not in self.topics.keys():
            self._register(key)
        if key in self.topics.keys():
            topic = self.topics[key]
            with self.lock:
                while not topic:
                    #print(f'{self} acquired topic, waiting for callbacks to be registered')
                    self.callbackCondition.wait()
            #print(f'{self} topic ready, executing call to topic {key}')
            topic(*args, **kwargs)

#############################################################################################

@singleton
class ThreadBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################

@singleton
class LockBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################

@singleton
class ConditionBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################

@singleton
class GeneralBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################