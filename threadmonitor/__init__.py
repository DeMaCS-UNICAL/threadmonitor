"""
TODO Insert general module description here
"""

from . import controller
from . import view

#print('proceeding to initialize View')
view.view_init()

def startGraph():
    """
    Inizializza le varie componenti del sistema, avviando il debugger grafico.
    """
    #print('proceeding to initialize Controller')
    controller.SingletonController().start()