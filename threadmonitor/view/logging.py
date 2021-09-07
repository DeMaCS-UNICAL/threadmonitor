from threadmonitor.utils import singleton
from threadmonitor.model.events import GeneralBroker, LockBroker, ThreadBroker, ConditionBroker
import logging
import datetime

def getTimestamp() -> str:
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

def getFormattedTime() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

class LoggingView:
    def __init__(self) -> None:
        pass

    def __printFormat(self, printStr):        
        logging.debug(f" [{ getFormattedTime() }] {printStr}")

    def start(self):
        self.__printFormat("System starting...")

    def mainloop(self):
        self.__printFormat("Graphic systems running.")

    def play(self):
        self.__printFormat("System execution mode set to: play") 

    def stop(self):
        self.__printFormat("System execution mode set to: debug")

    def next_step(self):
        self.__printFormat("Executing next instruction in debug execution mode")

    def newThread(self, thread):
        self.__printFormat(f"New thread { str(thread.ident) } running")

    def newLock(self, lock):
        self.__printFormat(f"New lock { str(lock.id) } available")

    def setWaitThread(self, thread, lock):
        self.__printFormat(f"Thread { str(thread.ident) } in wait on lock { str(lock.id) }")

    def drawFutureLockThread(self, thread, lock):
        pass

    def setAcquireThread(self, thread, lock):
        self.__printFormat(f"Thread { str(thread.ident) } acquiring lock { str(lock.id) }")

    def setAcquireThreadFromCondition(self, thread, lock, condition):
        self.__printFormat(f"Thread { str(thread.ident) } in condition { condition.id } acquiring lock { str(lock.id) }")

    def setReleaseThread(self, thread, lock):
        self.__printFormat(f"Thread { str(thread.ident) } released from lock { str(lock.id) }")

    def setThreadInCondition(self, thread, lock, condition):
        self.__printFormat(f"Thread { str(thread.ident) } waiting on condition { condition.id } of lock { str(lock.id) }") 

    def setLockName(self, lock, name):
        self.__printFormat(f"Changing lock { str(lock.id) } denomination to { name }")

    def newCondition(self, condition, lock):
        self.__printFormat(f"New condition { condition.id } from lock { lock.id }")

    def notifyLock(self, lock, condition, isAll):
        if isAll:
            self.__printFormat(f"Notifying all waiting threads from condition {condition.id} from lock { str(lock.id) }")
        else:
            self.__printFormat(f"Notifying a waiting thread from condition {condition.id} from lock { str(lock.id) }")

    def setConditionName(self, condition, lock, name):
        self.__printFormat(f"Changing condition {condition.id} from lock { str(lock.id) } denomination to {name}") 

@singleton
class SingletonLoggingView(LoggingView):
    pass

def setup() -> LoggingView:

    filename = f"logs/log_{ getTimestamp() }.txt.log"
    logging.basicConfig( level = logging.DEBUG, filename = filename )
    logging.debug(f"EXECUTION LOG {filename}")

    GeneralBroker().registerCallback('start', SingletonLoggingView().start)
    GeneralBroker().registerCallback('mainloop', SingletonLoggingView().mainloop)
    GeneralBroker().registerCallback('playBack', SingletonLoggingView().play)
    GeneralBroker().registerCallback('stopBack', SingletonLoggingView().stop)
    GeneralBroker().registerCallback('next_stepBack', SingletonLoggingView().next_step)

    ThreadBroker().registerCallback('add', SingletonLoggingView().newThread)

    LockBroker().registerCallback('add', SingletonLoggingView().newLock)
    LockBroker().registerCallback('setWaitThread', SingletonLoggingView().setWaitThread)
    LockBroker().registerCallback('drawFutureLockThread', SingletonLoggingView().drawFutureLockThread)
    LockBroker().registerCallback('setAcquireThread', SingletonLoggingView().setAcquireThread)
    LockBroker().registerCallback('setAcquireThreadFromCondition', SingletonLoggingView().setAcquireThreadFromCondition)
    LockBroker().registerCallback('setReleaseThread', SingletonLoggingView().setReleaseThread)
    LockBroker().registerCallback('setThreadInCondition', SingletonLoggingView().setThreadInCondition)
    LockBroker().registerCallback('setLockName', SingletonLoggingView().setLockName)

    ConditionBroker().registerCallback('add', SingletonLoggingView().newCondition)
    ConditionBroker().registerCallback('notifyLock', SingletonLoggingView().notifyLock)
    ConditionBroker().registerCallback('setConditionName', SingletonLoggingView().setConditionName)

    return SingletonLoggingView()




    