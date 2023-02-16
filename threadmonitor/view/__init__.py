"""
Il modulo view è dedicato alle differenti implementazioni di viste sull'esecuzione del codice.
Di default, è presente una vista grafica realizzata in Tk/Tcl.
E' presente anche una vista sperimentale che esegue logging su file delle varie operazioni.

E' possibile personalizzare il modulo view e aggiungere nuove viste procedendo come segue:

* creare un nuovo file nomeView.py all'interno del modulo
* implementare al suo interno un metodo setup(), seguendo l'esempio di quelli già esistenti
* modificare il metodo view_init, aggiungendo una chiamata al metodo nomeView.setup seguendo l'esempio di quelli già esistenti

"""

from . import tk
from . import logging

activeViews = []

def view_init():
    """Inizializza le varie view attive, conservando un riferimento al manager di ciascuna per garantire che il lifespan dell'oggetto corrisponda con quello dell'applicazione.
    """
    activeViews.append( tk.setup() )
    activeViews.append( logging.setup() )




