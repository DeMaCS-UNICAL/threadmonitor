# coding=utf-8

import threadmonitor.controller as controller
import threading as std_threading
import time
import os
from threadmonitor.utils import singleton

class _StopAndPlay:

    def __init__(self):
        self.lock = std_threading.Lock()
        self.condition = std_threading.Condition(self.lock)
        self.controller = controller.SingletonController()
        #verificare se è possibile rimuovere questa variabile
        self.running = True
        
    #TODO: capire il funzionamento di stop
    def stop(self):
        with self.lock:
            self.running = False

    #TODO: capire il funzionamento di play
    def play(self):
        with self.lock:
            self.running = True
            self.condition.notifyAll()
    
    def run(self):
        self.controller.run()

@singleton
class _SingletonStopAndPlay(_StopAndPlay):
    pass


class Lock():
    """
    Wrapper della classe Lock standard
    """

    __id = 1
    def __init__(self):
        # internal
        self.id = Lock.__id
        Lock.__id += 1
        # view
        self.controller = controller.SingletonController()
        self.controller.addLock(self)
        self.playController = _SingletonStopAndPlay()
        # wait
        self.waitLock = std_threading.Lock()
        self.waitCondition = std_threading.Condition(self.waitLock)
        # release
        self.releaseLock = std_threading.Lock()
        self.releaseCondition = std_threading.Condition(self.releaseLock)   
        self.isReleased = False     
        #true lock
        self.lock = std_threading.Lock()
        # non so a cosa afferiscono
        self.condionThread = {}
    
    def acquire( self, blocking = True, timeout = -1 ) -> bool:
        # sembra fare principalmente operazioni grafiche sotto waitLock
        with self.waitLock:
            self.isReleased = False
            self.playController.run()
            # puramente operazioni grafiche?
            sleepTime = self.controller.setWaitThread( current_thread(), self )
            time.sleep( sleepTime )
        # vera chiamata a threading.lock.acquire
        ret = self.lock.acquire( blocking, timeout )
        self.playController.run()
        self.controller.drawFutureLockThread( current_thread(), self )
        time.sleep(2)
        self.controller.setAcquireThread( current_thread(), self )
        time.sleep(3)
        # return della chiamata a threading.lock.acquire
        # problema di asincronia?
        return ret
    
    def release(self) -> None:
        # sembra fare principalmente operazioni grafiche sotto releaselock
        with self.releaseLock:
            if std_threading.current_thread() in self.condionThread.keys():
                self.controller.setAcquireThreadFromCondition( std_threading.current_thread(), self, self.condionThread[std_threading.current_thread()] )
                del self.condionThread[ std_threading.current_thread() ]
                time.sleep(3)
            self.playController.run()
            self.controller.setReleaseThread( std_threading.current_thread(), self )
            while not self.isReleased:
                self.releaseCondition.wait()
        # vero release?
        #TODO: accesso non protetto
        self.isReleased = False
        self.lock.release()
        time.sleep(2)

    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def addConditionThread(self,thread,condition) -> None:
        self.playController.run()
        self.controller.setThreadInCondition( thread, self, condition)
        self.condionThread[thread] = condition

    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def getId(self) -> int:
        return self.id
            
    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def setName( self, name ) -> None:
        self.controller.setLockName( self, name )


class Thread(std_threading.Thread):
    """
    Wrapper della classe Thread
    """

    def __init__(self, group = None, target = None, name = None, args = (), kwargs = {}, *, daemon = True):
        """
        default list of Thread.__init__ function arguments: necessario per garantire la retrocompatibilità
        """
        super().__init__(group = group, target = target, name = name, args = args, kwargs = kwargs, daemon = daemon)
        self.controller = controller.SingletonController()
        self.controller.addThread(self)
    
    #TODO: non-compliant colla libreria standard, da decidere come sostituirlo (exceptionhook?)
    def exit(self):
        os._exit(0)     


class Condition(std_threading.Condition):
    """
    Wrapper della classe Condition
    """

    #TODO: rendere la gestione dei lock trasparente all'utente
    def __init__(self,lock = None):
        super().__init__(lock)
        self.glock = lock
        self.controller = controller.SingletonController()
        self.name = ""
        self.controller.addCondition(self,self.glock)
        
    def wait(self, timeout = None) -> bool:
        self.glock.addConditionThread(std_threading.current_thread(),self)
        return super().wait(timeout)

    def wait_for(self, predicate, timeout = None) -> bool:
        self.glock.addConditionThread(std_threading.current_thread(),self)
        return super().wait_for(predicate, timeout)

    def notify(self, n = 1) -> None:
        self.controller.notifyLock(self.glock,self,False)
        super().notify(n)

    def notify_all(self) -> None:
        self.controller.notifyLock(self.glock,self,True)
        super().notify( len(self._waiters) )
    
    #TODO: non-compliant colla libreria standard, da decidere come sostituirlo
    def setName(self,name):
        self.controller.setConditionName(self,self.glock,name)


#TODO da valutare se qua si può utilizzare anche il Thread di libreria: reflection?
def current_thread() -> Thread:
    return std_threading.current_thread()

def get_ident() -> int:
    return std_threading.get_ident()

def get_native_id() -> int:
    return std_threading.get_native_id()