from graphthreading import Controller,GraphLock,GraphThread,GraphCondition
from threading import Thread,current_thread
from random import random,randrange
from time import sleep
import graphthreading


class Structure:
    def __init__(self):
        self.lock = GraphLock()
        self.condition = GraphCondition(self.lock)
        self.value = random()

    def get(self):
        self.lock.acquire()
        self.lock.release()


class MyThread(GraphThread):
    def __init__(self,structures):
        super().__init__()
        self.structures=structures
        
    
    def run(self):
        while True:
            i = randrange(len(self.structures))
            self.structures[1].get()
            sleep(randrange(3))


structures = [Structure() for i in range(5)]
threads = []

for i in range(4):
    MyThread(structures).start()
    	

graphthreading.startGraph()

