# coding=utf-8

from tkinter import ttk
from tkinter import *
from typing import Any, Optional, Tuple
from PIL import ImageTk
import threading
import time
from functools import partial
from threadmonitor.utils import getResourceFromName


def createAndEmplaceButton(master, text, command, **placeArgs) -> Button:
    ret = Button(master, text = text, command = command)
    ret.place(**placeArgs)
    return ret

def getPhotoImage(resourceName: str, resizeParams: Tuple[int, int], master) -> ImageTk.PhotoImage:
    image = ImageTk.Image.open( getResourceFromName(resourceName) )
    image = image.resize( resizeParams )
    return ImageTk.PhotoImage( master = master, image = image )


class AbstractContainer:
    def __init__(self, container: Canvas, image: PhotoImage, baseWidth, baseHeight) -> None:
        self.container = container
        self.image = image

        self.lock = threading.Lock()
        self.threads = []
        self.currentWidth = baseWidth
        self.currentHeight = baseHeight
    
    def add(self, thread, *args, **kwargs) -> None:
        with self.lock:
            self.threads.append(thread)
            self.drawNewThread(thread)
            self.postAdd(args = args, kwargs = kwargs)

    def remove(self, threadObject) -> None:
        with self.lock:
            if self.removeCondition(threadObject):
                for thread in self.threads:
                    self.deleteSingle(thread)
                self.threads.remove(threadObject)
                self.redrawThreads()

    def redrawThreads(self) -> None:
        for thread in self.threads:
            self.redrawSingle(thread)
        self.updatePosition()

    def drawNewThread(self, thread) -> None:
        self.redrawSingle(thread)

    def postAdd(self, *args, **kwargs) -> None:
        return

    def removeCondition(self, obj) -> bool:
        return True

    def redrawSingle(self, thread) -> None:        
        tag = str( thread.ident )
        self.container.create_image( self.currentWidth, self.currentHeight, image = self.image, tag = f'image{ tag }', anchor = 'n' )
        self.container.create_text( self.currentWidth, self.currentHeight, text = thread.getName(), tag = f'text{ tag }', anchor = 'n' )

    def deleteSingle(self, thread) -> None:
        tag = str(thread.ident)
        self.container.delete(f'image{ tag }')
        self.container.delete(f'text{ tag }')

    def updatePosition(self) -> None:
        return

    pass


class ConditionContainer:
    def __init__( self, conditionContainer, image, containerHeight, imageComputerHeight, imageComputerWidth, semCanvas, conditionLabel, semGreenCanvas ):
        self.container = conditionContainer
        self.lock = threading.Lock()
        self.conditionThreads = []
        self.currentWidth = 20
        self.image = image
        self.containerHeight = containerHeight
        self.imageComputerHeight = imageComputerHeight
        self.imageComputerWidth = imageComputerWidth
        self.semCanvas = semCanvas
        self.conditionLabel = conditionLabel
        self.semGreenCanvas = semGreenCanvas

    def setConditionLabel( self, name ):
        self.conditionLabel.configure( text = name )

    def addThreadInCondition( self, thread ):
        with self.lock:
            self.conditionThreads.append(thread)
            self.drawNewThread(thread)

    def removeThreadInCondition( self, threadObject ):
        with self.lock:
            if threadObject in self.conditionThreads:
                for thread in self.conditionThreads:
                    self.container.delete('image'+str(thread.ident))
                    self.container.delete('text'+str(thread.ident))
                self.conditionThreads.remove(threadObject)
                self.redrawThread()
    
    def redrawThread(self):
        currentWidth = 20
        imageHeight = 0 

        for thread in self.conditionThreads:
            tag=str(thread.ident)
            self.container.create_image(currentWidth,imageHeight,image=self.image,tag='image'+tag,anchor='n')
            self.container.create_text(currentWidth,imageHeight+(100/100)*self.imageComputerHeight,text=thread.getName(),tag='text'+tag,anchor="n")
            currentWidth+=self.imageComputerWidth*2
        self.currentWidth=currentWidth
    
    def drawNewThread(self,thread):
        tag = str(thread.ident)
        imageHeight = 0
        self.container.create_image(self.currentWidth,imageHeight,image=self.image,tag='image'+tag,anchor='n')
        self.container.create_text(self.currentWidth,imageHeight+(100/100)*self.imageComputerHeight,text=thread.getName(),tag='text'+tag,anchor="n",font="Times 10 ")
        self.currentWidth+=self.imageComputerWidth*2

    def blinkCondition(self,startTime,red,grey):
        updateCanvas = self.semCanvas if grey == "greyRedSem" else self.semGreenCanvas
        currentTime = time.time()
        if currentTime<=startTime+7:
            state = "hidden" if red else "normal"
            updateCanvas.itemconfigure(grey,state=state)
            updateCanvas.after(400,self.blinkCondition,startTime,not red,grey)
        else:
            updateCanvas.itemconfigure(grey,state='normal')


class InactiveContainer:
    def __init__(self,inactiveContainer,image):
        self.container = inactiveContainer
        self.lock = threading.Lock()
        self.inactiveThreads = []
        self.currentWidth = 0
        self.image = image

    def addThreadInactive(self,thread,lock):
        with self.lock:
            self.inactiveThreads.append(thread)
            self.drawNewThread(thread,lock)

    def removeThreadInactive(self,threadObject):
        with self.lock:
            if threadObject in self.inactiveThreads:
                for thread in self.inactiveThreads:
                    self.container.delete('image'+str(thread.ident))
                    self.container.delete('text'+str(thread.ident))
                self.inactiveThreads.remove(threadObject)
                self.redrawThread()
    
    def redrawThread(self):
        currentWidth = 0
        
        for thread in self.inactiveThreads:
            tag=str(thread.ident)
            self.container.create_image(currentWidth,30,image=self.image,tag='image'+tag,anchor='n')
            self.container.create_text(currentWidth,100,text=thread.getName(),tag='text'+tag,anchor="n")
            currentWidth+=100
        self.currentWidth=currentWidth
    
    #TODO: dipendenza dal wrapper, da risolvere
    def drawNewThread(self,thread,lock):
        #TODO: verificare perchè è stato aggiunto questo lock e se è possibile toglierlo
        lock.releaseLock.acquire()
        
        tag = str(thread.ident)
        self.container.create_image(self.currentWidth,30,image=self.image,tag='image'+tag,anchor='n')
        self.container.create_text(self.currentWidth,100,text=thread.getName(),tag='text'+tag,anchor='n')
        self.currentWidth +=100
        
        lock.releaseCondition.notify_all()
        lock.isReleased=True
        lock.releaseLock.release()


class WaitContainer:
    def __init__(self, wait_container: Canvas, image, imageHeight ):
        self.container = wait_container
        self.lock = threading.Lock()
        self.waitThreads = []
        self.currentHeight = 0
        self.image = image
        self.imageHeight = imageHeight
    
    def addThreadInWait(self,thread,lock) -> None:
        with self.lock:
            self.waitThreads.append(thread)
            self.drawNewThread(thread)
            lock.canAquire = True

    def removeThreadInWait( self, threadObject ) -> None:
        with self.lock:
            for thread in self.waitThreads:
                tag = str(thread.ident)
                self.container.delete( f"text{tag}" )
                self.container.delete( f"image{ str(thread.ident) }" )

            self.waitThreads.remove(threadObject)
            self.redrawThread()
    
    def redrawThread( self ) -> None:
        currentHeight = 0
        
        for thread in self.waitThreads:
        
            tag=str(thread.ident)
            currentWidth = int(self.container.winfo_width()/2)
            self.container.create_image(currentWidth, currentHeight, image = self.image, tag = 'image'+tag, anchor = 'n' )
            currentHeight += 1.2*self.imageHeight
            self.container.create_text(currentWidth, currentHeight, text = thread.getName(), tag = 'text'+tag, anchor = "n" )
            currentHeight += 0.5*self.imageHeight
        
        self.currentHeight = currentHeight
    
    def drawNewThread( self, thread ) -> None:
        tag = str(thread.ident)
        currentWidth = int(self.container.winfo_width()/2)
        self.container.create_image( currentWidth, self.currentHeight, image = self.image, tag = 'image'+tag, anchor = 'n' )
        self.currentHeight+=1.2*self.imageHeight
        self.container.create_text( currentWidth, self.currentHeight, text = thread.getName(), tag = 'text'+tag, anchor = "n" )
        self.currentHeight +=0.5*self.imageHeight

    def drawFutureAcquireThread( self, thread ) -> None:
        self.container.itemconfigure( f"text{ str(thread.ident) }", fill='#cd5b45' )