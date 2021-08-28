import threading
from threadmonitor.model.events import *
from threadmonitor.utils import singleton
import threading
import time
import threadmonitor.model.logic as model

class Controller:
    
    def __init__(self):
        self.stepLock = threading.Lock()
        self.stepCondition = threading.Condition(self.stepLock)
        
        self.started = False
        self.startLock = threading.Lock()
        self.startCondition = threading.Condition( self.startLock )

        print(f'{self} concurrency structures initialized')

        self.modelData = model.SingletonLogic()

        self.stopAndPlay = StopAndPlay(self)

        print(f'{self} => view initialization')
        GeneralBroker().send(key = 'init', play = self.play, stop = self.stop, next = self.next_step, close = self.__onclose)

    def play(self):
        with self.stepLock:
            GeneralBroker().send(key = 'play')
            self.stopAndPlay.play()
    
    def stop(self):
        with self.stepLock:
            GeneralBroker().send(key = 'stop')
            self.stopAndPlay.stop()

    def next_step(self):
        with self.stepLock:
            GeneralBroker().send(key = 'next')
            self.stopAndPlay.next_step()

    def changeThreadName( self, label, textField, menu, button ):
        ThreadBroker().send(key='changeThreadName', label=label, textField=textField, menu=menu, button=button)
        
    def addThread( self, thread ):
        self.modelData.getThreads().append(thread)
        ThreadBroker().send(key = 'add', thread=thread)

    def setLockName( self, lock, name ):
        LockBroker().send(key = 'setLockName', lock = lock, name = name)

    def addLock( self, lock ):
        LockBroker().send(key = 'add', lock = lock)        
        
    def addCondition( self, condition, lock ):
        ConditionBroker().send(key = 'add', condition = condition, lock = lock)

    #TODO: metodo non sincronizzato
    def setWaitThread( self, thread, lock ) -> float:
        
        if not self.started:
            self.startLock.acquire()
            while not self.started:
                self.startCondition.wait()
            self.startLock.release()
            time.sleep(0.05)

        response = LockBroker().sendAndRecieve(key = 'setWaitThread', thread = thread, lock = lock )

        sleepTime = next(x for x in response if isinstance(x, float)) 
        return sleepTime

    def setAcquireThread( self, thread, lock ):
        LockBroker().send(key = 'setAcquireThread', thread = thread, lock = lock)
    
    def setAcquireThreadFromCondition( self, thread, lock, condition ):
        LockBroker().send(key = 'setAcquireThreadFromCondition', thread = thread, lock = lock, condition = condition)

    def setThreadInCondition( self, thread, lock, condition ):
        LockBroker().send(key = 'setThreadInCondition', thread = thread, lock = lock, condition = condition )

    def setReleaseThread( self, thread, lock ) -> float:
        response = LockBroker().sendAndRecieve(key='setReleaseThread', thread = thread, lock = lock )
        sleepTime = next(x for x in response if isinstance(x, float)) 
        return sleepTime
        
    def drawFutureLockThread( self, thread, lock ) -> None:
        LockBroker().send(key='drawFutureLockThread', thread=thread, lock=lock)

    def notifyLock(self,lock,condition,isAll):
        ConditionBroker().send(key='notifyLock', lock = lock, condition = condition, isAll = isAll)
    
    def setConditionName(self, condition, lock, name):
        ConditionBroker().send(key='setConditionName', condition = condition, lock = lock, name = name)

    def start(self):
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

    def __onclose(self):
        GeneralBroker().send(key = 'destroy')
        for thread in self.modelData.getThreads():
            thread.exit()

    def run(self):
        with self.stepLock:
            self.stopAndPlay.run()


@singleton
class SingletonController(Controller):
    pass

class StopAndPlay:

    def __init__(self, controller: Controller):
        self.condition = controller.stepCondition
        self.isStopped = False
        self.step = 0

    def stop(self):
        self.isStopped = True

    def play(self):
        self.isStopped = False
        self.step = 0
        self.condition.notifyAll()

    def run(self):
        if self.isStopped:
            while self.isStopped and self.step <= 0:
                self.condition.wait()
            self.step -= 1

    def next_step(self):
        self.step += 1
        self.condition.notifyAll()