from lock import GraphLock
from controller import Controller
from threading import Thread
from time import sleep
import sys
import os

controller = Controller()

class Structure:
    def __init__(self,controller):
        self.lock = GraphLock(controller)
    
    def get(self):
        self.lock.acquire()
        self.lock.release()


class MyThread(Thread):
    def __init__(self,structure):
        super().__init__()
        self.structures=structure
    
    def run(self):
        while not Controller.FINISH:
            print(controller.FINISH)
            self.structures.get()
            sleep(5)

   


structure = Structure(controller)
threads = []
for i in range(3):
    t = MyThread(structure)
    threads.append(t)
    
controller.addThread(threads)
    
for t in threads:
    t.start()



controller.start()


