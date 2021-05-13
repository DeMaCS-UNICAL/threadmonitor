from graphthreading import Controller,GraphLock,GraphThread,GraphCondition
from threading import Thread,current_thread
from time import sleep
import graphthreading


class Structure:
    def __init__(self):
        self.lock = GraphLock()
        self.condition = GraphCondition(self.lock)
        self.lock.setName('lockName')
    
    def get(self):
        self.lock.acquire()
        self.lock.release()

class MyThread(GraphThread):
    def __init__(self,structure):
        super().__init__()
        self.structures=structure

    def run(self):
        while True:
            self.structures.get()
            
structure = Structure()
threads = []
lock=GraphLock()
lock2=GraphLock()
con = GraphCondition(lock)

lock3=GraphLock()
con3 = GraphCondition(lock)

lock4=GraphLock()
for i in range(4):
    t = MyThread(structure)
    threads.append(t)

for t in threads:
    t.start()

graphthreading.startGraph()





