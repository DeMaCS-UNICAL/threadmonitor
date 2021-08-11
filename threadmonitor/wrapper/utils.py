import threadmonitor.view.controllers as graph_view
import threading as std_threading

class _StopAndPlay:

    def __init__(self):
        self.lock = std_threading.Lock()
        self.condition = std_threading.Condition(self.lock)
        self.stepLock = graph_view.stepLock
        self.stepCondition = graph_view.stepCondition
        #verificare se è possibile rimuovere questa variabile
        self.running = True
        self.controller = graph_view.controller
    
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
        #TODO: acquisizione di un lock "globale"
        with self.stepLock:
            if self.controller.checkIfStopped():
                while self.controller.checkIfStopped(checkStepsToo = True):
                    self.stepCondition.wait()
                self.controller.decreaseStep()

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class _SingletonStopAndPlay(_StopAndPlay):
    pass
