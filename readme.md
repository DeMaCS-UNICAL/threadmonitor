Library originally made by Guido Scarlato, forked by Davide Caligiuri. Supervisor: Prof. Giovambattista Ianni

# GraphThreading

![](resource/application.PNG)

### Example
``` python 
# to obtain a perfectly valid multithreading code, replace with:
# from threading import Lock, Thread, Condition
from threadmonitor.wrapper.threading import Lock, Thread, Condition
import threadmonitor

class Structure:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
    
    def get(self):
        self.lock.acquire()
        self.lock.release()

class MyThread(Thread):
    def __init__(self,structure):
        super().__init__()
        self.structure = structure

    def run(self):
        while True:
            self.structure.get()

if __name__ == "__main__":            
    structure = Structure()
    threads = []

    for i in range(4):
        t = MyThread(structure)
        threads.append(t)

    for t in threads:
        t.start()

    threadmonitor.startGraph()

```
## Instructions
---
### Clone

- Clone this repo to your local machine using `https://github.com/Dygwah98/threadmonitor`
---
### Setup

> using pipenv (recommended):

```shell
sudo apt-get install python3-tk
pipenv install
```

> using pip:

```shell
sudo apt-get install python3-tk
pip3 install -r requirements.txt 
```

> using conda:

```shell
sudo apt-get install python3-tk
conda create --name p39 python=3.9
conda activate p39
conda install -c conda-forge --file requirements.txt
```

---
### Update documentation

Please, comment the call to view_init in the __init__.py of the root module before updating.
Comment it out when done to ensure the code works.

```shell
cd docs
make clean
make [html | epub | latex | ...] 
```
For more, refer to the [Sphinx documentation](https://www.sphinx-doc.org/en/master/man/sphinx-build.html).

---
### Execute tests

If using pipenv:

```shell
pipenv shell
# [testname] must be a suitable source file in the tests directory
# OMIT the .py at the end
python -m tests.[testname]
```

---
## Features
> Graphic representation of the components

> Start and stop the whole system

> Excecution step by step 

> Seamless integration with the existing threading module
