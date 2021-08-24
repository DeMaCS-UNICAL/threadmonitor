"""
TODO Insert general module description here
"""

from . import controller

def startGraph():
    """
    Inizializza il controller, avviando il debugger grafico.
    """
    controller.SingletonController().start()