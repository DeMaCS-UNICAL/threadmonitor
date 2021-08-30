from abc import abstractmethod
from typing import Any, KeysView
from threadmonitor.utils import singleton
import threading
import os

class LogicData:
    def __init__(self) -> None:

        ### lock per sincronizzare gli accessi alle risorse ###
        self.lock = threading.Lock()

        ### hashMap contenente come chiave il nome del lock, e come valore il relativo canvas ###
        self.lockContainer = {}

        ### wait container associato a uno specifico lock ###
        self.waitContainer = {}

        ### Lista dei threads ###
        self.threads = []

    def getLockContainerKeys(self) -> KeysView:
        with self.lock:
            return self.lockContainer.keys()

    def getLockData(self, key) -> Any:
        with self.lock:
            return self.lockContainer[key]

    def addLockData(self, key, value) -> None:
        with self.lock:
            self.lockContainer[key] = value

    def getWaitContainerKeys(self) -> KeysView:
        with self.lock:
            return self.waitContainer.keys()
    
    def getWaitData(self, key) -> Any:
        with self.lock:
            return self.waitContainer[key]

    def addWaitData(self, key, value) -> None:
        with self.lock:
            self.waitContainer[key] = value

    def getThreads(self) -> list:
        with self.lock:
            return self.threads

    def removeThread(self, thread) -> None:
        with self.lock:
            self.threads.remove(thread)


@singleton
class SingletonLogic(LogicData):
    pass


class AbstractContainer:
    """
    Classe base per la gestione di liste di thread da visualizzare.
    """
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.threads = []
    
    def add(self, thread, lock = None) -> None:
        with self.lock:
            self.threads.append(thread)
            self.drawSingle(thread, lock)
            self.postAdd(thread, lock)

    def remove(self, threadObject) -> None:
        with self.lock:
            if self.removeCondition(threadObject):
                for thread in self.threads:
                    self.deleteSingle(thread)
                self.threads.remove(threadObject)
                self.redrawAll()

    #TODO: definire se sia necessario il lock sul redraw
    def redrawAll(self) -> None:
        for thread in self.threads:
            self.redrawSingle(thread)

    #TODO: definire se sia necessario il lock sul redraw
    def drawSingle(self, thread, lock = None) -> None:
        self.redrawSingle(thread)

    def removeCondition(self, obj) -> bool:
        return True

    @abstractmethod
    def redrawSingle(self, thread) -> None:        
        pass

    @abstractmethod
    def deleteSingle(self, thread) -> None:
        pass

    def postAdd(self, thread, lock) -> None:
        return

class LogicThreadInterface(threading.Thread):
    """
    Wrapper della classe Thread
    """

    def __init__(self, group = None, target = None, name = None, args = (), kwargs = {}, *, daemon = True):
        """
        default list of Thread.__init__ function arguments: necessario per garantire la retrocompatibilità
        """
        super().__init__(group = group, target = target, name = name, args = args, kwargs = kwargs, daemon = daemon)
    
    def exit(self):
        os._exit(0)