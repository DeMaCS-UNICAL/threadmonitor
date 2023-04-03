import threading
import copy
from typing import Any
from threadmonitor.utils import singleton


class _Topic(list):
    """Rappresentazione di un topic, o argomento di conversazione fra più entità.
    L'implementazione consiste in una lista di callbacks, ciascuna rappresentante la reazione di una particolare entità
    al messaggio consegnato.
    """
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        with self.lock:
            ret = [f(*args, **kwargs) for f in self]
            return ret

    def __repr__(self):
        return "Topic(%s)" % list.__repr__(self)


class Broker:
    """Manager di una particolare tipologia di topic, astrae le operazioni principali da fare su di esso e garantisce la corretta sincronizzazione.
    """
    def __init__(self, topicType: _Topic) -> None:
        self.topics = {}
        self.lock = threading.Lock()
        self.callbackCondition = threading.Condition(self.lock)
        self.topicType = topicType

    def _register(self, key: str):
        """Se assente, crea un topic identificato dal valore fornito.

        :param key: l'identificativo del nuovo topic.
        """
        with self.lock:
            if key not in self.topics.keys():
                self.topics[key] = self.topicType()

    def registerTopic(self, key: str):
        """Wrapper del metodo _register.

        :param key: l'identificativo del nuovo topic.
        """
        self._register(key)
            
    def registerCallback(self, key, callback, register = True):
        """Registra una funzione come callback all'interno del topic identificato dalla key.

        :param key: l'identificativo del topic.
        :param callback: la callback da registrare.
        :param register: se True, crea il topic nel caso sia assente.
        """
        if register and key not in self.topics.keys():
            self._register(key)
        with self.lock:
            self.topics[key].append(callback)
            self.callbackCondition.notifyAll()

    def sendAndReceive(self, key: str, register = True, *args, **kwargs) -> list:
        """Invia un messaggio al topic indicato dalla key fornita, restituendo il risultato di tutte le callback eseguite in risposta.

        :param key: l'identificativo del topic.
        :param register: se True, crea il topic nel caso sia assente.
        :param args: componenti senza identificativo del messaggio inviato.
        :param kwargs: componenti con identificativo del messaggio inviato.

        :returns: lista dei risultati di tutte le callback eseguite in risposta.
        """
        if register and key not in self.topics.keys():
            self._register(key)
        if key in self.topics.keys():
            topic = self.topics[key]
            with self.lock:
                while not topic:
                    self.callbackCondition.wait()
            return copy.deepcopy( topic(*args, **kwargs) )
        return []

    def send(self, key: str, register = True, *args, **kwargs) -> None:
        """Invia un messaggio al topic indicato dalla key fornita. Questo metodo non restituisce alcun risultato,
        per quello vedere sendAndReceive.

        :param key: l'identificativo del topic.
        :param register: se True, crea il topic nel caso sia assente.
        :param args: componenti senza identificativo del messaggio inviato.
        :param kwargs: componenti con identificativo del messaggio inviato.
        """
        if register and key not in self.topics.keys():
            self._register(key)
        if key in self.topics.keys():
            topic = self.topics[key]
            with self.lock:
                while not topic:
                    self.callbackCondition.wait()
            topic(*args, **kwargs)

#############################################################################################

@singleton
class ThreadBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################

@singleton
class LockBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################

@singleton
class ConditionBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################

@singleton
class GeneralBroker(Broker):
    def __init__(self) -> None:
        super().__init__(_Topic)

#############################################################################################