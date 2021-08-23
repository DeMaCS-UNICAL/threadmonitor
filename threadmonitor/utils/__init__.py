import os

def getResourceFromName(filename: str) -> str:
    for r,d,f in os.walk(".."):
        for files in f:
            if files == filename:
                #print(os.path.join(r,files))
                return os.path.join(r,files)

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance