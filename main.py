from graphthreading import Controller,GraphLock,GraphThread,GraphCondition
from threading import Thread,current_thread
from time import sleep
import graphthreading


class Structure:
    def __init__(self):
        self.lock = GraphLock()
        self.condition = GraphCondition(self.lock)
        self.condition.setName('test')
        self.lock.setName('test')
    
    def get(self):
        self.lock.acquire()
        self.lock.release()


class MyThread(GraphThread):
    def __init__(self,structure,sctructure2,structure3):
        super().__init__()
        self.structures=structure
        self.structure2 = sctructure2
        self.structure3 = structure3
        
    
    def run(self):
        while True:
            self.structures.get()
            sleep(5)
            self.structure2.get()
            sleep(5)
            self.structure3.get()
            sleep(5)

   


structure = Structure()
structure2 = Structure()
structure3 = Structure()



threads = []

for i in range(4):
    t = MyThread(structure,structure2,structure3)
    threads.append(t)

    
    


for t in threads:
    t.start()




graphthreading.startGraph()





