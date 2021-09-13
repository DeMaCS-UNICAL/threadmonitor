from time import sleep
from random import randrange
from threadmonitor import startGraph
from threadmonitor.wrapper.threading import Thread,Lock,Condition


class Bacchetta:
    def __init__(self):
        #self.lock = Lock()
        self.occupata = False

    def checkOccupata(self):
        return self.occupata

    def prendiBacchetta(self):
        #self.lock.acquire()
        self.occupata = True
    
    def lasciaBacchetta(self):
        #self.lock.release()
        self.occupata = False

class Tavolo:

    def __init__(self):
        self.bacchetta = [Bacchetta() for _ in range(5)]
        self.lock = Lock()
        self.cond = Condition(self.lock)

    #
    #  Questo metodo (non usato), consentirebbe di prendere le bacchette, mangiare e lasciare
    #  le bacchette in un solo colpo
    #  Tuttavia non consente a più di un filosofo per volta di mangiare, poichè self.lock rimane acquisito
    #  per tutta la durata del pasto.
    #
    def prendiMangiaESmetti(self,posizione):

        self.lock.acquire()
        while( self.bacchetta[posizione].checkOccupata() or self.bacchetta[(posizione+1) % 5].checkOccupata() ):
            self.cond.wait()
        self.bacchetta[posizione].prendiBacchetta()
        self.bacchetta[(posizione+1) % 5].prendiBacchetta()

        #
        # 
        #
        sleep(1)
        #
        #
        #

        self.bacchetta[posizione].lasciaBacchetta()
        self.bacchetta[(posizione+1) % 5].lasciaBacchetta()
        self.cond.notifyAll()
        self.lock.release()

    def prendiLockSimultaneo(self,posizione):
        
        try:
            self.lock.acquire()
            while( self.bacchetta[posizione].checkOccupata() or self.bacchetta[(posizione+1) % 5].checkOccupata() ):
                self.cond.wait()
            self.bacchetta[posizione].prendiBacchetta()
            self.bacchetta[(posizione+1) % 5].prendiBacchetta()
            self.lock.release()
        except Exception as e:
            print(e)

    def mollaLockSimultaneo(self,posizione):

        try:
            self.lock.acquire()
            self.bacchetta[posizione].lasciaBacchetta()
            self.bacchetta[(posizione+1) % 5].lasciaBacchetta()
            self.cond.notifyAll()
            self.lock.release()
        except Exception as e:
            print(e)

class Filosofo(Thread):
    
    def __init__(self,tavolo,pos):
        super().__init__()
        self.posizione = pos
        self.t = tavolo
        self.name = "Philip %s" % pos
    
    def attesaCasuale(self,msec):
        sleep(randrange(msec)/1000.0)

    def pensa(self):
        print(f"Il filosofo {self.getName()} pensa.")
        #sleep(2)
        #self.attesaCasuale(2000)
        print(f"Il filosofo {self.getName()} smette di pensare.")
        
    def mangia(self):

        #self.t.prendiMangiaESmetti(self.posizione)
        print(f"Il filosofo {self.getName()} vuole mangiare.")
        
        # Acquire di entrambe le bacchette
        self.t.prendiLockSimultaneo(self.posizione)
        print(f"Il filosofo {self.getName()} ha le sue bacchette e mangia.")
        
        self.attesaCasuale(1)

        # Release di entrambe le bacchette
        print(f"Il filosofo {self.getName()} sta per lasciare le sue bacchette.")
        self.t.mollaLockSimultaneo(self.posizione)

        print(f"Il filosofo {self.getName()} termina di mangiare.")

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
