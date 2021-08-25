# coding=utf-8

from abc import abstractmethod
from tkinter import *
from typing import Any, Optional, Tuple
from PIL import ImageTk
import threading
import time
from threadmonitor.utils import getResourceFromName, overrides
import threadmonitor.model as model


def createAndEmplaceButton(master, text, command, **placeArgs) -> Button:
    """
    Istanzia e restituisce un Button creato con i parametri forniti.
    E' possibile personalizzare ulteriormente il Button creato utilizzando i metodi configure() e place().
    """
    ret = Button(master, text = text, command = command)
    ret.place(**placeArgs)
    return ret

def getPhotoImage(resourceName: str, resizeParams: Tuple[int, int], master) -> ImageTk.PhotoImage:
    """
    Istanzia e restituisce una PhotoImage con i parametri forniti.
    """
    image = ImageTk.Image.open( getResourceFromName(resourceName) )
    image = image.resize( resizeParams )
    return ImageTk.PhotoImage( master = master, image = image )


class AbstractTkContainer(model.AbstractContainer):
    
    def __init__(self, container: Canvas, image: PhotoImage, baseWidth, baseHeight) -> None:
        super().__init__()
        self.container = container
        self.image = image

        self.currentWidth = baseWidth
        self.currentHeight = baseHeight


class ConditionContainer(AbstractTkContainer):
    
    def __init__( self, conditionContainer: Canvas, image: PhotoImage, containerHeight, imageComputerHeight, imageComputerWidth, semCanvas, conditionLabel, semGreenCanvas ):
        super().__init__(conditionContainer, image, 20, 0)
        self.containerHeight = containerHeight
        self.imageComputerHeight = imageComputerHeight
        self.imageComputerWidth = imageComputerWidth
        self.semCanvas = semCanvas
        self.conditionLabel = conditionLabel
        self.semGreenCanvas = semGreenCanvas

    def setConditionLabel( self, name ):
        self.conditionLabel.configure( text = name )

    def blinkCondition(self, startTime, red, grey):
        updateCanvas = self.semCanvas if grey == "greyRedSem" else self.semGreenCanvas
        currentTime = time.time()
        if currentTime <= startTime + 7:
            state = "hidden" if red else "normal"
            updateCanvas.itemconfigure( grey, state = state )
            updateCanvas.after( 400, self.blinkCondition, startTime, not red, grey )
        else:
            updateCanvas.itemconfigure( grey, state = 'normal' )
    
    @overrides(AbstractTkContainer)
    def redrawAll(self) -> None:
        self.currentWidth = 20
        return super().redrawAll()

    @overrides(AbstractTkContainer)
    def removeCondition(self, obj) -> bool:
        return obj in self.threads

    @overrides(AbstractTkContainer)
    def redrawSingle(self, thread) -> None:
        tag = str(thread.ident)
        self.container.create_image( self.currentWidth, self.currentHeight, image = self.image, tag = f'image{tag}', anchor = 'n' )
        self.container.create_text( self.currentWidth, self.currentHeight + self.imageComputerHeight, text = thread.getName(), tag = f'text{tag}', anchor = 'n' )
        self.currentWidth += self.imageComputerWidth*2

    @overrides(AbstractTkContainer)
    def deleteSingle(self, thread) -> None:
        tag = str(thread.ident)
        self.container.delete(f'image{ tag }')
        self.container.delete(f'text{ tag }')


class InactiveContainer(AbstractTkContainer):
    
    def __init__(self, inactiveContainer: Canvas, image: PhotoImage):
        super().__init__(inactiveContainer, image, 0, 30)

    #TODO: dipendenza dal wrapper, da risolvere
    @overrides(AbstractTkContainer)
    def drawSingle(self, thread, lock):
        #TODO: verificare perchè è stato aggiunto questo lock e se è possibile toglierlo
        lock.releaseLock.acquire()
        
        super().drawSingle(thread)
        
        lock.releaseCondition.notify_all()
        lock.isReleased=True
        lock.releaseLock.release()

    @overrides(AbstractTkContainer)
    def redrawAll(self) -> None:
        self.currentWidth = 0
        return super().redrawAll()

    @overrides(AbstractTkContainer)
    def removeCondition(self, obj) -> bool:
        return obj in self.threads

    @overrides(AbstractTkContainer)
    def deleteSingle(self, thread) -> None:
        tag = str(thread.ident)
        self.container.delete(f'image{tag}')
        self.container.delete(f'text{tag}')

    @overrides(AbstractTkContainer)
    def redrawSingle(self, thread) -> None:
        tag=str(thread.ident)
        self.container.create_image( self.currentWidth, self.currentHeight, image = self.image, tag = f'image{tag}', anchor = 'n' )
        self.container.create_text( self.currentWidth, self.currentHeight + 70, text = thread.getName(), tag=f'text{tag}', anchor = 'n' )
        self.currentWidth += 100


class WaitContainer(AbstractTkContainer):
    
    def __init__(self, wait_container: Canvas, image, imageHeight ):
        super().__init__(wait_container, image, 0, 0)
        self.imageHeight = imageHeight
    
    def drawFutureAcquireThread( self, thread ) -> None:
        self.container.itemconfigure( f"text{ str(thread.ident) }", fill='#cd5b45' )

    @overrides(AbstractTkContainer)
    def redrawAll(self) -> None:
        self.currentHeight = 0
        return super().redrawAll()

    @overrides(AbstractTkContainer)
    def redrawSingle(self, thread) -> None:
        tag=str(thread.ident)
        self.currentWidth = int(self.container.winfo_width()/2)
        self.container.create_image( self.currentWidth, self.currentHeight, image = self.image, tag = f'image{tag}', anchor = 'n' )
        self.currentHeight += 1.2*self.imageHeight
        self.container.create_text( self.currentWidth, self.currentHeight, text = thread.getName(), tag = f'text{tag}', anchor = "n" )
        self.currentHeight += 0.5*self.imageHeight

    @overrides(AbstractTkContainer)
    def deleteSingle(self, thread) -> None:
        tag = str(thread.ident)
        self.container.delete( f"text{tag}" )
        self.container.delete( f"image{tag}" )

    @overrides(AbstractTkContainer)
    def postAdd(self, thread, lock) -> None:
        lock.canAcquire = True
