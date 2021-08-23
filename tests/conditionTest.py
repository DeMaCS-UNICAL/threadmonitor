from threadmonitor.wrapper.threading import Lock,Thread,Condition
from time import sleep
from threadmonitor.controller import startGraph

class Structure:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.condition2 = Condition(self.lock)
        self.condition3 = Condition(self.lock)
        self.number=3
    
    def minNumber(self):
        self.lock.acquire()
        self.number-=3
        if self.number == 0:
            self.condition2.notify()
        self.lock.release()
    
    def addNumber(self):
        self.lock.acquire()
        while self.number>0:
            self.condition2.wait()
        print('add')
        self.number+=1
        self.lock.release()

class MyThread(Thread):
    def __init__(self,structure):
        super().__init__()
        self.structure = structure
    
    def run(self):
        self.structure.minNumber()
        sleep(5)

class TestThread(Thread):
    def __init__(self,structure):
        super().__init__()
        self.structure = structure
    
    def run(self):
        for i in range(100):
            self.structure.addNumber()
            print(self.structure.number)

if __name__ == "__main__":
    structure = Structure()

    t1 = MyThread(structure)
    t2 = MyThread(structure)
    t3 = MyThread(structure)

    test = TestThread(structure)
    test.start()

    t2.start()
    t3.start()
    t1.start()

    startGraph()

    t2.join()
    t3.join()
    t1.join()

    test.join()