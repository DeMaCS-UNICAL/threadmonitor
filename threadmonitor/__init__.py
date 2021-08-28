"""
TODO Insert general module description here
"""

import time
from . import controller
from . import view

def startGraph():
    """
    Inizializza le varie componenti del sistema, avviando il debugger grafico.
    """
    print('proceeding to initialize View')
    view.view_init()
    print('proceeding to initialize Controller')
    controller.SingletonController().start()

startGraph()