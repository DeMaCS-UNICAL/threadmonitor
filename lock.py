from threading import Lock
from threading import current_thread
from time import sleep
class GraphLock:
    def __init__(self,controller):
        self.lock=Lock()
        self.controller = controller
        
    def acquire(self):
        self.controller.addWaitThread(current_thread().getName())
        self.lock.acquire()
        print('Lock presolo',current_thread().getName())
        self.controller.setThreadWithLock(current_thread().getName())
        print('FIne lock preso',current_thread().getName())
        sleep(3)
        
    def release(self):
        self.lock.release()




