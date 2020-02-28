from graphthreading import Controller,GraphLock,GraphThread,GraphCondition
from threading import Thread,current_thread
from time import sleep
import graphthreading

class Structure:
    def __init__(self):
        self.lock = GraphLock()
        self.condition = GraphCondition(self.lock)
        self.condition2 = GraphCondition(self.lock)
        self.condition3 = GraphCondition(self.lock)
        self.number=3
    
    def minNumber(self):
        self.lock.acquire()
        self.number-=3
        if self.number ==0:
            self.condition2.notify()
        self.lock.release()
    
    def addNumber(self):
        self.lock.acquire()
        while self.number>0:
            self.condition2.wait()
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
test.start()




t2.start()
#t3.start()
#t1.start()


graphthreading.startGraph()