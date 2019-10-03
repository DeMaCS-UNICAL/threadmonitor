import graphthreading
from graphthreading import Controller,GraphLock
from threading import Thread
from time import sleep
import sys
import os



class Structure:
    def __init__(self):
        self.lock = GraphLock()
    
    def get(self):
        self.lock.acquire()
        self.lock.release()


class MyThread(graphthreading.GraphThread):
    def __init__(self,structure):
        super().__init__()
        self.structures=structure
        
    
    def run(self):
        while not Controller.FINISH:
            self.structures.get()
            sleep(5)

   


structure = Structure()
threads = []
for i in range(3):
    t = MyThread(structure)
    threads.append(t)
    
    
    


for t in threads:
    t.start()



graphthreading.startGraph()


