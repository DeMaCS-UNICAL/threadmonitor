"""
Il modulo utils contiene metodi di utilità generici, non legati a nessun particolare modulo.
"""

import os
import threading

def getResourceFromName(filename: str) -> str:
    """
    Restituisce il path del file cercato, se presente nella directory un livello superiore a quello d'esecuzione.

    :param filename: il nome del file che si cerca.

    :returns: il path del file cercato.
    """
    for r,d,f in os.walk(".."):
        for files in f:
            if files == filename:
                return os.path.join(r,files)

def singleton(class_):
    """Annotazione (detta anche decorator) custom.
    Fa si che ogni chiamata al costruttore generi un'unica istanza della classe annotata.
    
    :param class: la classe che va istanziata una singola volta.
    """
    instances = {}
    lock = threading.Lock()
    def _getinstance(*args, **kwargs):
        if class_ not in instances:
            with lock:
                if class_ not in instances:
                    instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return _getinstance

def overrides(interface_class):
    """Annotazione (detta anche decorator) custom.
    Verifica che il metodo annotato sia un override di uno dei metodi della classe indicata.
    
    :param interface_class: la classe che subisce l'override.
    """
    def _overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return _overrider