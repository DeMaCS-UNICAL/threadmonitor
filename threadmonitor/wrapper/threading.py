# coding=utf-8

from threadmonitor.model.logic import LogicThreadInterface
import threadmonitor.controller as controller
import threading as std_threading
import time


class Lock():
    """
    Wrapper della classe threading.Lock.
    """

    __id = 1
    def __init__( self ):
        """Inizializza il wrapper, registrandolo sul Controller.
        """
        # internal
        self.id = Lock.__id
        Lock.__id += 1
        # view
        self.controller = controller.SingletonController()
        #print(f'{self} attempting to register to Controller')
        self.controller.addLock(self)
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
        """Wrapper del metodo threading.Lock.acquire.
        Internamente, contattata il Controller per indicargli le operazioni da far eseguire.
        
        :param blocking: definisce se il metodo deve essere bloccante. Default: True.
        :param timeout: se specificato, definisce il massimo tempo per cui il metodo deve essere bloccante.

        :returns: stessi valori di threading.Lock.acquire.
        """
        with self.waitLock:
            self.isReleased = False
            self.controller.run()
            sleepTime = self.controller.setWaitThread( current_thread(), self )
            time.sleep( sleepTime )
        # vera chiamata a threading.lock.acquire
        ret = self.lock.acquire( blocking, timeout )
        self.controller.run()
        self.controller.drawFutureLockThread( current_thread(), self )
        time.sleep(2)
        self.controller.setAcquireThread( current_thread(), self )
        time.sleep(3)
        # return della chiamata a threading.lock.acquire
        return ret
    
    def release( self ) -> None:
        """Wrapper del metodo threading.Lock.release.
        Internamente, contattata il Controller per indicargli le operazioni da far eseguire.
        """
        # sembra fare principalmente operazioni grafiche sotto releaselock
        with self.releaseLock:
            if std_threading.current_thread() in self.condionThread.keys():
                self.controller.setAcquireThreadFromCondition( std_threading.current_thread(), self, self.condionThread[std_threading.current_thread()] )
                del self.condionThread[ std_threading.current_thread() ]
                time.sleep(3)
            self.controller.run()
            self.controller.setReleaseThread( std_threading.current_thread(), self )
            while not self.isReleased:
                self.releaseCondition.wait()
        # vero release?
        #TODO: accesso non protetto
        self.isReleased = False
        self.lock.release()
        time.sleep(2)

    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def addConditionThread( self, thread, condition ) -> None:
        """Questo metodo non è pensato per l'uso diretto, ma solo come handle per altre componenti della libreria.

        :param thread: Il thread che entra in wait sulla condition indicata.
        :param condition: La condition su cui entra in wait il thread indicato.
        """
        self.controller.run()
        self.controller.setThreadInCondition( thread, self, condition)
        self.condionThread[thread] = condition

    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def getId( self ) -> int:
        """Questo metodo non è pensato per l'uso diretto, ma solo come handle per altre componenti della libreria.

        :returns: L'id del lock.
        """
        return self.id
            
    #TODO: non-compliant colla libreria standard, da decidere se sostituirlo
    def setName( self, name: str ) -> None:
        """Questo metodo non è pensato per l'uso diretto, ma solo come handle per altre componenti della libreria.

        :param name: Il nuovo nome del lock.
        """
        self.controller.setLockName( self, name )


class Thread(LogicThreadInterface):
    """
    Wrapper della classe threading.Thread.
    """

    def __init__( self, group = None, target = None, name = None, args = (), kwargs = {}, *, daemon = True ):
        """Inizializza il wrapper, registrandolo sul Controller.
        I parametri sono gli stessi di threading.Thread.__init__ per garantire la compatibilità con codici esistenti.

        :param group: Parametro riservato per utilizzi futuri. Non utilizare.
        :param target: Callback eseguita all'interno del metodo run. Alternativa all'override del metodo.
        :param name: Nome assegnato al Thread.
        :param daemon: Se True, il thread viene terminato quando termina il processo che lo ha creato. Default: True.
        """
        super().__init__(group = group, target = target, name = name, args = args, kwargs = kwargs, daemon = daemon)
        self.controller = controller.SingletonController()
        self.controller.addThread(self)


class Condition(std_threading.Condition):
    """
    Wrapper della classe threading.Condition.
    """

    __id = 1
    def __init__( self, lock = None ):
        """Inizializza il wrapper, registrandolo sul Controller.

        :param lock: Il lock a cui la Condition fa riferimento.
        """
        super().__init__(lock)
        self.id = Condition.__id
        Condition.__id += 1
        self.glock = lock
        self.controller = controller.SingletonController()
        self.name = ""
        self.controller.addCondition(self,self.glock)
        
    def wait( self, timeout = None ) -> bool:
        """Wrapper del metodo threading.Condition.wait.

        :param timeout: Se specificato, indica il tempo massimo durante il quale il metodo è bloccante.
        """
        self.glock.addConditionThread(std_threading.current_thread(),self)
        return super().wait(timeout)

    def wait_for( self, predicate, timeout = None ) -> bool:
        """Wrapper del metodo threading.Condition.wait_for.

        :param predicate: Specifica la condizione da soddisfare perchè il metodo rilasci.
        :param timeout: Se Specificato, indica il tempo massimo durante il quale il metodo è bloccante.
        """
        self.glock.addConditionThread(std_threading.current_thread(),self)
        return super().wait_for(predicate, timeout)

    def notify( self, n = 1 ) -> None:
        """Wrapper del metodo threading.Condition.notify.

        :param n: #TODO
        """
        self.controller.notifyLock(self.glock,self,False)
        super().notify(n)

    def notify_all( self ) -> None:
        """Wrapper del metodo threading.Condition.notify_all.
        """
        self.controller.notifyLock(self.glock,self,True)
        super().notify( len(self._waiters) )
    
    #TODO: non-compliant colla libreria standard, da decidere come sostituirlo
    def setName( self, name: str ):
        """Questo metodo non è pensato per l'uso diretto, ma solo come handle per altre componenti della libreria.

        :param name: il nuovo nome della Condition.
        """
        self.controller.setConditionName(self,self.glock,name)


def current_thread() -> std_threading.Thread:
    """Wrapper del metodo threading.current_thread.
    """
    return std_threading.current_thread()

def get_ident() -> int:
    """Wrapper del metodo threading.get_ident.
    """
    return std_threading.get_ident()

def get_native_id() -> int:
    """Wrapper del metodo threading.get_native_id.
    """
    return std_threading.get_native_id()