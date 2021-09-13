"""
ThreadMonitor è una libreria per il debugging grafico di programmi multithreaded; può essere integrato agilmente all'interno di
un programma esistente, offrendo la possibilità di interrompere l'esecuzione e di visualizzare le interazioni fra Lock, Thread, e Condition,
semplificando la comprensione dei motivi di errore e inconsistenza (deadlock, starvation, etc.).

COME INTEGRARLO

* cambiare ogni import da threading in import da threadmonitor.wrapper.threading
* aggiungere una chiamata al metodo threadmonitor.startGraph() alla fine del main

"""

from . import controller
from . import view

#view.view_init()

def startGraph():
    """
    Inizializza le varie componenti del sistema, avviando il debugger grafico.
    """
    #print('proceeding to initialize Controller')
    controller.SingletonController().start()