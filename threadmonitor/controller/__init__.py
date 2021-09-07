from threadmonitor.model.events import *
from threadmonitor.utils import singleton
import threading
import time
import threadmonitor.model.logic as model

class Controller:
    
    def __init__(self):
        self.stepLock = threading.Lock()
        self.stepCondition = threading.Condition( self.stepLock ) 
        
        self.started = False
        self.startLock = threading.Lock()
        self.startCondition = threading.Condition( self.startLock )

        self.modelData = model.SingletonLogic()
        self.stopAndPlay = StopAndPlay(self)

        GeneralBroker().registerCallback('playBack', self.play)
        GeneralBroker().registerCallback('stopBack', self.stop)
        GeneralBroker().registerCallback('next_stepBack', self.next_step)

    def play(self):
        #print(f'starting play controller-side')
        self.stopAndPlay.play()
    
    def stop(self):
        #print(f'starting stop controller-side')
        self.stopAndPlay.stop()

    def next_step(self):
        self.stopAndPlay.next_step()

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
        
    def run(self):
        self.stopAndPlay.run()
        
    def addThread( self, thread ):
        self.modelData.getThreads().append(thread)
        ThreadBroker().send(key = 'add', thread=thread)

    def addLock( self, lock ):
        LockBroker().send(key = 'add', lock = lock)        
        
    def addCondition( self, condition, lock ):
        ConditionBroker().send(key = 'add', condition = condition, lock = lock)

    def setLockName( self, lock, name ):
        LockBroker().send(key = 'setLockName', lock = lock, name = name)

    def setWaitThread( self, thread, lock ) -> float:
        if not self.started:
            with self.startLock:
                while not self.started:
                    self.startCondition.wait()
            time.sleep(0.05)

        response = LockBroker().sendAndReceive(key = 'setWaitThread', thread = thread, lock = lock )

        sleepTime = next(x for x in response if isinstance(x, float)) 
        return sleepTime

    def setAcquireThread( self, thread, lock ):
        LockBroker().send(key = 'setAcquireThread', thread = thread, lock = lock)
    
    def setAcquireThreadFromCondition( self, thread, lock, condition ):
        LockBroker().send(key = 'setAcquireThreadFromCondition', thread = thread, lock = lock, condition = condition)

    def setThreadInCondition( self, thread, lock, condition ):
        LockBroker().send(key = 'setThreadInCondition', thread = thread, lock = lock, condition = condition )

    def setReleaseThread( self, thread, lock ) -> float:
        response = LockBroker().sendAndReceive(key = 'setReleaseThread', thread = thread, lock = lock )
        sleepTime = next(x for x in response if isinstance(x, float)) 
        return sleepTime
        
    def drawFutureLockThread( self, thread, lock ) -> None:
        LockBroker().send(key = 'drawFutureLockThread', thread = thread, lock = lock)

    def notifyLock(self,lock,condition,isAll):
        ConditionBroker().send(key = 'notifyLock', lock = lock, condition = condition, isAll = isAll)
    
    def setConditionName(self, condition, lock, name):
        ConditionBroker().send(key = 'setConditionName', condition = condition, lock = lock, name = name)


@singleton
class SingletonController(Controller):
    pass

class StopAndPlay:

    def __init__(self, controller: Controller):
        self.lock = controller.stepLock
        self.condition = controller.stepCondition
        self.isStopped = False
        self.step = 0

    def stop(self):
        with self.lock: 
            self.isStopped = True

    def play(self):
        with self.lock:
            self.isStopped = False
            self.step = 0
            self.condition.notifyAll()

    def run(self):
        with self.lock:
            if self.isStopped:
                while self.isStopped and self.step <= 0:
                    self.condition.wait()
                self.step -= 1

    def next_step(self):
        with self.lock:
            self.step += 1
            self.condition.notifyAll()