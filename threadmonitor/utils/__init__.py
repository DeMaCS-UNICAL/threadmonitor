import os
import threading

def getResourceFromName(filename: str) -> str:
    """
    Restituisce il path del file cercato, se presente nella directory un livello superiore a quello d'esecuzione.
    """
    for r,d,f in os.walk(".."):
        for files in f:
            if files == filename:
                #print(os.path.join(r,files))
                return os.path.join(r,files)

def singleton(class_):
    """
    Fa si che ogni chiamata al costruttore generi un'unica istanza della classe annotata.
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

def threadBound(class_):
    """
    """
    instances = {}
    def _getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return _getinstance

def overrides(interface_class):
    """
    Verifica che il metodo annotato sia un override di uno dei metodi della classe indicata.
    """
    def _overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return _overrider