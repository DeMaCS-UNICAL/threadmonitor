import threadmonitor
from threadmonitor.wrapper.threading import Lock,Thread,Condition
from random import random,randrange
from time import sleep

class Structure:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.value = random()

    def get(self):
        self.lock.acquire()
        self.lock.release()

class MyThread(Thread):
    def __init__( self, structures: list ):
        super().__init__( daemon = True )
        self.structures = structures
        
    def run(self):
        while True:
            i = randrange( len(self.structures) - 1 )
            self.structures[i].get()
            sleep(randrange(3))

if __name__ == "__main__":
    structures = [ Structure() for i in range(5) ]
    threads = [ MyThread(structures) for i in range(16) ]

    for thr in threads:
        thr.start()

    #TODO: eliminare la necessità di un avvio esplicito della vista
    threadmonitor.startGraph()

    for thr in threads:
        thr.join()