import tm_graph.view.graph_view as graph_view
import threading
import time
import os

#
# lock della libreria: wrapper sulla classe Lock standard
#

class Lock:
    __id = 1
    def __init__(self):
        # internal
        self.id = Lock.__id
        Lock.__id += 1
        # view
        self.controller = graph_view.controller
        self.controller.addLock(self)
        self.playController = graph_view._StopAndPlay()
        # wait
        self.waitLock = threading.Lock()
        self.waitCondition = threading.Condition(self.waitLock)
        # A CHE CAZZO SERVE
        self.isInWait = False
        # release
        self.releaseLock = threading.Lock()
        self.releaseCondition = threading.Condition(self.releaseLock)   
        self.isReleased = False     
        # ???
        self.lockCondition = threading.Lock()
        self.condCondition = threading.Condition(self.lockCondition)
        # true lock?
        self.lock = threading.Lock()
        # non so a cosa afferiscono
        self.canAcquire = False
        self.condionThread = {}
    
    #quale lock si comporta come il lock vero? dove passare i parametri?
    def acquire(self, blocking=True, timeout=-1) -> bool:
        # ???
        # sembra fare principalmente operazioni grafiche sotto waitLock
        with self.waitLock:
            self.isReleased = False
            self.playController.run()
            # puramente operazioni grafiche?
            sleepTime = self.controller.setWaitThread(threading.current_thread(),self)
            time.sleep(sleepTime)
        # vero acquire?
        # è sicuro ritornare direttamente il risultato della chiamata?
        ret = self.lock.acquire(blocking, timeout)
        self.playController.run()
        self.controller.drawFutureLockThread(threading.current_thread(),self)
        time.sleep(2)
        self.controller.setAcquireThread(threading.current_thread(),self)
        time.sleep(3)
        return ret
    
    #quale lock si comporta come il lock vero? dove passare i parametri?
    def release(self) -> None:
        # ???
        # sembra fare principalmente operazioni grafiche sotto releaselock
        with self.releaseLock:
            if threading.current_thread() in self.condionThread.keys():
                self.controller.setAcquireThreadFromCondition(threading.current_thread(),self,self.condionThread[threading.current_thread()])
                del self.condionThread[threading.current_thread()]
                time.sleep(3)
            self.playController.run()
            self.controller.setReleaseThread(threading.current_thread(),self)
            while not self.isReleased:
                self.releaseCondition.wait()
        # vero release?
        self.isReleased = False
        self.lock.release()
        time.sleep(2)

    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def addConditionThread(self,thread,condition):
        self.playController.run()
        self.controller.setThreadInCondition(thread,self,condition)
        self.condionThread[thread] = condition

    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def getId(self):
        return self.id
            
    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def setName(self,name):
        self.controller.setLockName(self,name)

#
# thread della libreria
#

class Thread(threading.Thread):
    # default list of Thread.__init__ function arguments: necessario per garantire la retrocompatibilità
    def __init__(self, _group = None, _target = None, _name = None, _args = (), _kwargs = {}, *, _daemon = True):
        super().__init__(group=_group, target=_target, name=_name, args=_args, kwargs=_kwargs, daemon=_daemon)
        self.controller = graph_view.controller
        self.controller.addThread(self)
    
    #TODO: non-compliant colla libreria standard, da decidere come sostituirlo (exceptionhook?)
    def exit(self):
        os._exit(0)     

#
# condition della libreria
#

class Condition(threading.Condition):
    #TODO: rendere la gestione dei lock trasparente all'utente
    def __init__(self,lock = None):
        super().__init__(lock)
        self.glock = lock
        self.controller = graph_view.controller
        self.name = ""
        self.controller.addCondition(self,self.glock)
        
    def wait(self, timeout = None) -> bool:
        self.glock.addConditionThread(threading.current_thread(),self)
        return super().wait(timeout)

    def wait_for(self, predicate, timeout = None) -> bool:
        self.glock.addConditionThread(threading.current_thread(),self)
        return super().wait_for(predicate, timeout)

    def notify(self, n = 1) -> None:
        self.controller.notifyLock(self.glock,self,False)
        super().notify(n)

    def notifyAll(self) -> None:
        self.controller.notifyLock(self.glock,self,True)
        super().notify(len(self._waiters))
    
    #TODO: non-compliant colla libreria standard, da decidere come sostituirlo
    def setName(self,name):
        self.controller.setConditionName(self,self.glock,name)

#da valutare se qua si può utilizzare anche il Thread di libreria
#reflection?
def current_thread() -> threading.Thread:
    return threading.current_thread()

def get_ident() -> int:
    return threading.get_ident()

def get_native_id() -> int:
    return threading.get_native_id()