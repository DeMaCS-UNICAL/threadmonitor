from tm_graph.logic.graph_logic import Lock,Thread,Condition
from random import random,randrange
from time import sleep
from tm_graph.view.graph_view import startGraph

class Structure:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.value = random()

    def get(self):
        self.lock.acquire()
        self.lock.release()

class MyThread(Thread):
    def __init__(self,structures):
        super().__init__()
        self.structures=structures
        
    
    def run(self):
        while True:
            i = randrange(len(self.structures) - 1)
            self.structures[i].get()
            sleep(randrange(3))

structures = [Structure() for i in range(5)]
threads = []

for i in range(16):
    MyThread(structures).start()

startGraph()