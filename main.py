import graphthreading
from graphthreading import Controller,GraphLock,GraphThread
from threading import Thread,current_thread
from time import sleep
import sys
import os


'''
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
        while True:
            self.structures.get()
            sleep(5)

   


structure = Structure()
threads = []

for i in range(4):
    t = MyThread(structure)
    threads.append(t)

    
    


for t in threads:
    t.start()

'''

class MyThread(GraphThread):
    def __init__(self,lock1,lock2):#,lock3,lock4)
        super().__init__()
        self.lock1=lock1
        self.lock2=lock2
        '''
        self.lock3 = lock3
        self.lock4 = lock4
        '''

       
    
    def run(self):
        self.lock1.acquire()
        sleep(10)
        self.lock1.release()

        print(current_thread().getName(),'sta acquisendo il lock 2')
        self.lock2.acquire()

        sleep(12)
        self.lock2.release()
        '''
        self.lock3.acquire()
        sleep(12)
        self.lock3.release()
        self.lock4.acquire()
        sleep(12)
        self.lock4.release()
        '''

lock1=GraphLock()
lock2=GraphLock()
'''
lock3=GraphLock()
lock4=GraphLock()
'''
mt = MyThread(lock1,lock2)#,lock3,lock4)
m2 = MyThread(lock1,lock2)#,lock3,lock4)
m3 = MyThread(lock1,lock2)#,lock3,lock4)
m4 = MyThread(lock1,lock2)#,lock3,lock4)

m5 = MyThread(lock1,lock2)#,lock3,lock4)
m6 = MyThread(lock1,lock2)#,lock3,lock4)
m7 = MyThread(lock1,lock2)#,lock3,lock4)
m8 = MyThread(lock1,lock2)#,lock3,lock4)
m9 = MyThread(lock1,lock2)#,lock3,lock4)
m10 = MyThread(lock1,lock2)#,lock3,lock4)




mt.start()
m2.start()
m3.start()
m4.start()

m5.start()
m6.start()
m7.start()
m8.start()
m9.start()
m10.start()

graphthreading.startGraph()





