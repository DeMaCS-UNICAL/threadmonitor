from library.graphthreading import Controller,GraphLock,GraphThread,GraphCondition
from threading import Thread,current_thread
from time import sleep
from library import graphthreading

class Structure:
    def __init__(self):
        self.lock = GraphLock()
        self.condition = GraphCondition(self.lock)
        self.number=3
    
    def minNumber(self):
        self.lock.acquire()
        self.number-=1
        if self.number ==0:
            self.condition.notifyAll()
        self.lock.release()
    
    def addNumber(self):
        self.lock.acquire()
        while self.number>0:
            self.condition.wait()
        print('add')
        self.number+=1
        self.lock.release()

class MyThread(GraphThread):
    def __init__(self,structure):
        super().__init__()
        self.structure = structure
    
    def run(self):
        self.structure.minNumber()
        sleep(5)

class TestThread(GraphThread):
    def __init__(self,structure):
        super().__init__()
        self.structure = structure
    
    def run(self):
        self.structure.addNumber()
        print(self.structure.number)
structure = Structure()

t1 = MyThread(structure)
t2 = MyThread(structure)
t3 = MyThread(structure)

test = TestThread(structure)

t2.start()
t3.start()
test.start()
t1.start()


graphthreading.startGraph()