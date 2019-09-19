from lock import GraphLock
from controller import Controller
from threading import Thread
from time import sleep

class Structure:
    def __init__(self,controller):
        self.lock = GraphLock(controller)
    
    def get(self):
        self.lock.acquire()
        self.lock.release()


class MyThread(Thread):
    def __init__(self,structure):
        super().__init__()
        self.structure=structure
    
    def run(self):
        while True:
            structure.get()
            sleep(5)

controller = Controller()

structure = Structure(controller)
threads = []
for i in range(5):
    t = MyThread(structure)
    threads.append(t)
    
for t in threads:
    t.start()


controller.start()
