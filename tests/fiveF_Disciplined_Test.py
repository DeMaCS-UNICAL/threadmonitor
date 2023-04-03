
from threadmonitor import startGraph
from threadmonitor.wrapper.threading import Thread,Lock,Condition
from time import sleep
from random import randrange,random


class Bacchetta:
    
    def __init__(self):
        self.lock = Lock()

    def lasciaBacchetta(self):
        self.lock.release()
        
    def prendiBacchetta(self):
        self.lock.acquire()

class Tavolo:

    def __init__(self):
        self.bacchetta = [Bacchetta() for _ in range(5)]

class Filosofo(Thread):
    
    def __init__(self,tavolo,pos):
        super().__init__()
        self.posizione = pos
        self.t = tavolo
        self.name = "Philip %s" % pos

    def attesaCasuale(self,msec):
        sleep(randrange(msec)/1000.0)

    def mangia(self):
        print(f"Il filosofo {self.getName()} vuole mangiare")
        
        ## SOLUZIONE AI PROBLEMI DI DEADLOCK
        minPos, maxPos = self.posizione, (self.posizione + 1) % 5
        if minPos > maxPos:
            minPos, maxPos = maxPos, minPos
        ##

        self.t.bacchetta[minPos].prendiBacchetta()
        print(f"Il filosofo {self.getName()} prende prima bacchetta")

        self.t.bacchetta[maxPos].prendiBacchetta()
        print(f"Il filosofo {self.getName()} prende seconda bacchetta e comincia a mangiare.")
        
        #
        # Attende per un tempo casuale che simula il tempo di elaborazione passato a mangiare
        #
        self.attesaCasuale(1)
        
        print(f"Il filosofo {self.getName()}  termina di mangiare.")
        
        self.t.bacchetta[maxPos].lasciaBacchetta()
        print(f"Il filosofo {self.getName()}  lascia prima bacchetta.")
        
        self.t.bacchetta[minPos].lasciaBacchetta()
        print(f"Il filosofo {self.getName()} lascia seconda bacchetta.")

    def pensa(self):
        print(f"Il filosofo {self.getName()} pensa.")
        
        #
        # Attende per un tempo casuale che simula il tempo di elaborazione passato a pensare
        #
        self.attesaCasuale(1)
        
        print(f"Il filosofo {self.getName()} smette di pensare.")


    def run(self):
        while True:
            self.pensa()
            self.mangia()


if __name__ == "__main__":
    tavolo = Tavolo()
    filosofi = [Filosofo(tavolo,i) for i in range(5)]
    for f in filosofi:
        f.start()

    startGraph()

    for f in filosofi:
        f.join()

