import os
from typing import Union

def getResourceFromName(filename: str) -> str:
    for r,d,f in os.walk(".."):
        for files in f:
            if files == filename:
                #print(os.path.join(r,files))
                return os.path.join(r,files)