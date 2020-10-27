Library made by Guido Scarlato.

# GraphThreading

![](application.PNG)

### Example
``` python 
from graphthreading import Controller,GraphLock,GraphThread,GraphCondition
import graphthreading


class Structure:
    def __init__(self):
        self.lock = GraphLock()
        self.condition = GraphCondition(self.lock)
        self.lock.setName('lockName')
    
    def get(self):
        self.lock.acquire()
        self.lock.release()

class MyThread(GraphThread):
    def __init__(self,structure):
        super().__init__()
        self.structure=structure

    def run(self):
        while True:
            self.structure.get()
            
structure = Structure()
threads = []

for i in range(4):
    t = MyThread(structure)
    threads.append(t)

for t in threads:
    t.start()

graphthreading.startGraph()
```

---
### Clone

- Clone this repo to your local machine using `https://github.com/guidoscarl/threadmonitor.git`
---
### Setup

> install python packages

```shell
sudo apt-get install python3-tk
pip3 install Pillow 
```


---

## Features
> Graphic representation of the components

> Start and stop the whole system

> Excecution step by step 




