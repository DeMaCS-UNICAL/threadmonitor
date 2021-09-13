"""Il modulo controller si occupa di orchestrare le varie funzionalità del sistema in maniera sincrona.
Per fare questo, fa uso di una serie di topic standard (già implementati) per comunicare con le altre componenti, in particolare con le view.

I segnali pre-implementati sono i seguenti:

GeneralBroker signals:

* 'start': indica l'avvio effettivo del sistema
* 'mainloop': indica l'avvio del mainloop per le view che lo necessitano (Tk/Tcl)
* 'playBack': aggiunto per retrocompatibilità con la view Tk
* 'stopBack': aggiunto per retrocompatibilità con la view Tk
* 'next_stepBack': aggiunto per retrocompatibilità con la view Tk

ThreadBroker signals:

* 'add': indica l'aggiunta di un nuovo thread al sistema

LockBroker signals:

* 'add': indica l'aggiunta di un nuovo lock al sistema
* 'setWaitThread': aggiunto per retrocompatibilità con la view Tk
* 'drawFutureLockThread': aggiunto per retrocompatibilità con la view Tk
* 'setAcquireThread': aggiunto per retrocompatibilità con la view Tk
* 'setAcquireThreadInCondition': aggiunto per retrocompatibilità con la view Tk
* 'setReleaseThread': aggiunto per retrocompatibilità con la view Tk
* 'setThreadInCondition': aggiunto per retrocompatibilità con la view Tk 
* 'setLockName': aggiunto per retrocompatibilità con la view Tk

ConditionBroker signals:

* 'add': indica l'aggiunta di una nuova condition al sistema
* 'notifyLock': aggiunto per retrocompatibilità con la view Tk
* 'setConditionName': aggiunto per retrocompatibilità con la view Tk

"""

from threadmonitor.model.events import *
from threadmonitor.utils import singleton
import threading
import time
import threadmonitor.model.logic as model

class Controller:
    """Classe che astrae tutte le variazioni di stato del sistema.
    Ogniqualvolta qualcosa accade all'interno del sistema, esso viene segnalato al Controller, che si occupa di comunicarlo
    al resto del sistema tramite i Broker (vedi threadmonitor.model.events).
    Inoltre, il controller si occupa della sincronizzazione fra le varie operazioni e della corretta gestione della concorrenza.
    """
    
    def __init__( self ):
        self.stepLock = threading.Lock()
        self.stepCondition = threading.Condition( self.stepLock ) 
        
        self.started = False
        self.startLock = threading.Lock()
        self.startCondition = threading.Condition( self.startLock )

        self.modelData = model.SingletonLogic()
        self.isStopped = False
        self.step = 0

        GeneralBroker().registerCallback('playBack', self.play)
        GeneralBroker().registerCallback('stopBack', self.stop)
        GeneralBroker().registerCallback('next_stepBack', self.next_step)

    def play( self ):
        """Riporta il codice nel normale flusso di esecuzione.
        """
        with self.stepLock:
            self.isStopped = False
            self.step = 0
            self.stepCondition.notifyAll()
    
    def stop( self ):
        """Interrompe l'esecuzione del codice.
        """
        with self.stepLock: 
            self.isStopped = True

    def next_step( self ):
        """Esegue la successiva funzione. Valido solo mentre il codice è interrotto.
        """
        with self.stepLock:
            self.step += 1
            self.stepCondition.notifyAll()

    def start( self ):
        """Avvia il sistema.
        """
        try:
            self.startLock.acquire()
            GeneralBroker().send(key = 'start')
            self.started = True
            
        except Exception as e:
            print(e)
        finally:
            self.startCondition.notifyAll()
            self.startLock.release()
            GeneralBroker().send(key = 'mainloop')
        
    def run( self ):
        """Esegue un'istruzione, o attende nel caso il sistema sia stato stoppato.
        """
        with self.stepLock:
            if self.isStopped:
                while self.isStopped and self.step <= 0:
                    self.stepCondition.wait()
                self.step -= 1
        
    def addThread( self, thread ):
        """Registra il nuovo thread all'interno del sistema.

        :param thread: il Thread appena creato.
        """
        self.modelData.getThreads().append(thread)
        ThreadBroker().send(key = 'add', thread=thread)

    def addLock( self, lock ):
        """Registra il nuovo lock all'interno del sistema.

        :param lock: il Lock appena creato.
        """
        LockBroker().send(key = 'add', lock = lock)        
        
    def addCondition( self, condition, lock ):
        """Registra la nuova condition all'interno del sistema.

        :param condition: la Condition appena creata.
        :param lock: il lock a cui la condition afferisce.
        """
        ConditionBroker().send(key = 'add', condition = condition, lock = lock)

    def setLockName( self, lock, name: str ):
        """Modifica il nome con cui il lock viene identificato a schermo.

        :param lock: il lock oggetto della modifica.
        :param name: il nuovo nome del lock.
        """
        LockBroker().send(key = 'setLockName', lock = lock, name = name)

    def setWaitThread( self, thread, lock ) -> float:
        """Rappresenta il cambio di stato del thread, da idle a waiting.

        :param thread: il thread che sta andando in wait sul lock.
        :param lock: il lock oggetto di wait.
        """
        if not self.started:
            with self.startLock:
                while not self.started:
                    self.startCondition.wait()
            time.sleep(0.05)

        response = LockBroker().sendAndReceive(key = 'setWaitThread', thread = thread, lock = lock )

        sleepTime = next(x for x in response if isinstance(x, float)) 
        return sleepTime

    def setAcquireThread( self, thread, lock ):
        """Rappresenta il cambio di stato del thread, facendolo passare da waiting ad acquire.

        :param thread: il thread che sta acquisendo il lock.
        :param lock: il lock acquisito.
        """
        LockBroker().send(key = 'setAcquireThread', thread = thread, lock = lock)
    
    def setAcquireThreadFromCondition( self, thread, lock, condition ):
        """
        """
        LockBroker().send(key = 'setAcquireThreadFromCondition', thread = thread, lock = lock, condition = condition)

    def setThreadInCondition( self, thread, lock, condition ):
        """Rappresenta il cambio di stato del thread, facendolo passare da waiting sul lock a waiting sulla condition.

        :param thread: il thread che sta andando in wait sulla condition.
        :param lock: il lock interessato.
        :param condition: la condition oggetto di wait.
        """
        LockBroker().send(key = 'setThreadInCondition', thread = thread, lock = lock, condition = condition )

    def setReleaseThread( self, thread, lock ) -> float:
        """Rappresenta il cambio di stato del thread, facendolo passare da acquire a release.

        :param thread: il thread che sta lasciando il lock.
        :param lock: il lock interessato.
        """
        response = LockBroker().sendAndReceive(key = 'setReleaseThread', thread = thread, lock = lock )
        sleepTime = next(x for x in response if isinstance(x, float)) 
        return sleepTime
        
    def drawFutureLockThread( self, thread, lock ) -> None:
        """
        """
        LockBroker().send(key = 'drawFutureLockThread', thread = thread, lock = lock)

    def notifyLock( self, lock, condition, isAll: bool ):
        """Sveglia uno o più thread in attesa su una determinata condition.

        :param lock: Il lock della condition interessata.
        :param condition: La condition interessata.
        :param isAll: se True, è necessario svegliare tutti i threads.
        """
        ConditionBroker().send(key = 'notifyLock', lock = lock, condition = condition, isAll = isAll)
    
    def setConditionName( self, condition, lock, name: str ):
        """Modifica il nome della condition fornita con la stringa fornita.

        :param condition: La condition interessata.
        :param lock: Il lock della condition interessata.
        :param name: Il nuovo nome della condition.
        """
        ConditionBroker().send(key = 'setConditionName', condition = condition, lock = lock, name = name)


@singleton
class SingletonController(Controller):
    pass