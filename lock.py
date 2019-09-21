from threading import Lock
from threading import current_thread
from time import sleep
class GraphLock:
    def __init__(self,controller):
        self.lock=Lock()
        self.controller = controller
    
    def acquire(self):
        """Acquire method, take the lock and update controller interface"""
        self.controller.addWaitThread(current_thread().getName())
        self.lock.acquire()
        print('Lock preso',current_thread().getName())
        self.controller.setThreadWithLock(current_thread().getName())
        sleep(5)
        
    def release(self):
        """Release method, release the lock and update controller interface"""
        self.lock.release()
        self.controller.releaseThread(current_thread().getName())




