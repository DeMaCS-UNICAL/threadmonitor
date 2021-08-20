from threadmonitor.wrapper.threading import Lock, Thread, Condition, get_ident
from time import sleep
from threadmonitor.view.tk import startGraph
import threading

printLock = threading.Lock()

class Structure:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
        #self.lock.setName('test')
    
    def print_get(self):
        with printLock:
            self.lock.acquire()
            print(f"lock acquired by {get_ident()}")
            self.lock.release()
            print(f"lock released by {get_ident()}")

    def std_get(self):
        self.lock.acquire()
        self.lock.release()

    def get(self):
        #self.print_get()
        self.std_get()

class MyThread(Thread):
    def __init__(self,structure,structure2,structure3):
        super().__init__()
        self.structures = structure
        self.structure2 = structure2
        self.structure3 = structure3
        
    def run(self):
        while True:
            self.structures.get()
            sleep(5)
            self.structure2.get()
            sleep(5)
            self.structure3.get()
            sleep(5)

if __name__ == "__main__":
    structure1 = Structure()
    structure2 = Structure()
    structure3 = Structure()

    threads = []

    for i in range(4):
        t = MyThread(structure3,structure2,structure1)
        threads.append(t)

    for t in threads:
        t.start()

    startGraph()