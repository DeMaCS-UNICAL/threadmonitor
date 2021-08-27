# coding=utf-8

from threadmonitor.model.events import ConditionEventHandler, GeneralEventHandler, LockEventHandler, ThreadEventHandler
from tkinter import ttk
from tkinter import * 
from typing import Any, Optional, Tuple
from PIL import ImageTk
import time
from threadmonitor.utils import getResourceFromName, overrides
import threadmonitor.model.logic as model
import threading


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


class TkView:
    def __init__(self):

        self.modelData = model.SingletonLogic()
        self.started = False
        self.startLock = threading.Lock()
        self.startCondition = threading.Condition( self.startLock )

        self.window = Tk()
        self.window.title( 'graphthreading' )

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_heigth = self.window.winfo_screenheight()
        self.pad = 3
        self.window.geometry( '{0}x{1}'.format( self.screen_width-self.pad, self.screen_heigth-self.pad ) )

        ### PUNTI DI PARTENZA DEI CONTAINERS ###
        self.currentOrientPosition = 0
        self.currentHeightPosition = 200

        self.currentHeightLeftPosition = 200
        self.currentHeightRightPosition = 200
        
        self.containerWidth = self.screen_width/5
        self.containerHeight = 200
        self.conditionHeight = (40/100)*self.containerHeight
        self.waitHeight = (30/100)*self.containerHeight
        self.lockHeight = (70/100)*self.containerHeight
        self.inactiveWidth = 500

        self.releasingLock = []
       
        ### Lista di tutti i container creati ###
        self.containers = []

        ### Contiene come chiave gli scroll, e come valore gli oggetti a cui sono attaccati ###
        self.scrolls = []

        self.conditions = []
       
        ### Inizializzazione inactive Frame ###
        
        #self.inactiveFrame=Frame(self.window,background='#ff1a1a')
        #self.inactiveFrame.pack(fill=BOTH)
        
        ### Inizializzazione primaryCanvas ###

        self.frame = Frame( self.window, width = self.screen_width, height = self.screen_heigth, background = 'grey' )
        self.frame.pack( fill = BOTH, expand = True )

        self.primaryCanvas = Canvas( self.frame, background = '#A0A0A0', highlightthickness = 0, highlightbackground = "black", height = 10000, width = self.screen_width )

        self.window.update_idletasks()

        self.yscroll = Scrollbar( self.frame, orient = VERTICAL )
        self.yscroll['command'] = self.primaryCanvas.yview
        self.yscroll.pack( side = RIGHT, fill = Y )

        self.primaryCanvas['yscrollcommand'] = self.yscroll.set
        self.primaryCanvas.pack( fill = BOTH, expand = True )

        self.inactiveCanvas = Canvas( self.primaryCanvas, background = 'white', highlightthickness = 1, highlightbackground = "black", height = 150, width = self.inactiveWidth )

        self.changeThreadButton = Button( self.inactiveCanvas, text = "Change thread name", command = None )
        self.changeThreadButton.place( relx = 0.5, rely = 0, anchor = 'n' )

        self.inactiveScroll = ttk.Scrollbar( self.inactiveCanvas, orient = HORIZONTAL, command = self.inactiveCanvas.xview )
        self.inactiveScroll.place( relx = 0.5, rely = 0.93, width = 305, anchor = 'center' )

        self.inactiveCanvas.configure( xscrollcommand = self.inactiveScroll.set )
        #self.inactiveCanvas.pack(anchor='center',pady=10)
        self.background = getPhotoImage('background.png', (10000, self.screen_width), self.primaryCanvas)
        #self.primaryCanvas.create_image(0,0,image=self.background,anchor='n')

        self.primaryCanvas.create_window( self.screen_width/2, 0, window = self.inactiveCanvas, anchor = 'n' )

        self.playButton = createAndEmplaceButton( self.primaryCanvas, 'play', None, relx = 0.93, rely = 0.02, relheight = 0.025 )
        self.stopButton = createAndEmplaceButton( self.primaryCanvas, 'pause', None, relx = 0.93, rely = 0.045, relheight = 0.025 )
        self.nextStepButton = createAndEmplaceButton( self.primaryCanvas, 'next step', None, relx = 0.93, rely = 0.070, relheight = 0.025 )
        self.nextStepButton.configure( state = 'disabled' )

        ### Inizializzazioni immagini ###
        self.imageComputerHeight = 32
        self.imageComputerWidth = 32
        self.computerImage = getPhotoImage( 'computer.png', (self.imageComputerHeight, self.imageComputerHeight), self.primaryCanvas )
        self.redSem = getPhotoImage( 'redSem.png', (15, 15), self.primaryCanvas )
        self.greenSem = getPhotoImage( 'greenSem.png', (15, 15), self.primaryCanvas )
        self.greySem = getPhotoImage( 'greySem.png', (15, 15), self.primaryCanvas )
        
        self.inactiveData = InactiveContainer( self.inactiveCanvas, self.computerImage )

        self.updateCommand = None

    def play(self):
        self.stopButton.configure( state = 'normal' )
        self.nextStepButton.configure( state = 'disabled' )
        self.primaryCanvas.configure( background = '#A0A0A0' )

    def stop(self):
        self.playButton.configure( state = 'normal' )
        self.nextStepButton.configure( state = 'normal' )
        self.primaryCanvas.configure( background = '#696969' )

    def newThread(self):
        pass

    def newLock(self, lock):
        ### creo il container e lo aggiungo alla lista di container ###
        
        container = Canvas( self.primaryCanvas, background = 'white', highlightthickness = 1, highlightbackground = "black", height = self.containerHeight, width = self.containerWidth )
                
        self.containers.append( container )

        ### creo il container che mostra il thread che ha acquisito il lock ###
        lock_container = Canvas( container, background = 'white', width = self.containerWidth, height = self.lockHeight )
        lockLabel = Label( lock_container, text = 'Lock '+ str( lock.getId() ) )
        lockLabel.place( relx = 0.5, rely = 0.80, anchor = 'center' )
        container.create_window( self.containerWidth/2, (30/100)*self.containerHeight, window = lock_container, anchor = 'n' )
        
        ### creo il container che mostra i thread in wait ###
        waitContainer = Canvas( container, background = '#fff7dc', highlightthickness = 1, highlightbackground = "black", width = self.containerWidth, height = self.waitHeight )
        container.create_window( self.containerWidth/2, (0/100)*self.containerHeight, window = waitContainer, anchor = 'n' )#.place(relx=0.5,anchor='center',rely=0.25, relheight=0.50,relwidth=1)
        waitLabel = Label( waitContainer,text = 'Wait threads' )
        waitLabel.place( relx = 0, rely = 0, anchor = 'nw' )
        self.modelData.addWaitData(lock, waitContainer)

        ### creo i semafori che mostrano lo stato attuale del lock ###
        lock_container.create_image( self.containerWidth*(90/100), self.containerHeight*(50/100), image = self.redSem, tag = "redSem", state = "hidden" )
        lock_container.create_image( self.containerWidth*(90/100), self.containerHeight*(50/100), image = self.greySem, tag = "greyRedSem" )

        lock_container.create_image( self.containerWidth*(90/100), self.containerHeight*(60/100), image = self.greenSem, tag = "greenSem" )
        lock_container.create_image( self.containerWidth*(90/100), self.containerHeight*(60/100), image = self.greySem, tag = "greyGreenSem", state = "hidden" )

        ### creo lo scroll del canvas per i thread in wait ###
        scroll = Scrollbar( waitContainer, orient = VERTICAL, command = waitContainer.yview )
        scroll.place( relx = 1, rely = 0.5, relheight = 1, anchor = 'e' )
        waitContainer.configure( yscrollcommand = scroll.set )
        self.scrolls.append( scroll )
        
        wait_data = WaitContainer( waitContainer, self.computerImage, self.imageComputerHeight )

        ### associo al lock i relativi container ###
        conditionContainers = {}
        currentHeightCanvas = self.containerHeight

        ### aggiorno le variabili per il posizionamento ###
        self.currentOrientPosition += 1

    def newCondition(self, condition, lock):
         ### prendo il container principale del lock a cui è associata la condition ###
        container_data = self.modelData.getLockData(lock)
        lock_container = container_data[7]

        ### prendo i dati utili a creare la window per la condition ###
        current_height = container_data[6]
        current_height += self.conditionHeight
        container_data[6] = current_height
        lock_container.configure( height = current_height )

        ### prendo il container delle condition associate al lock ###
        conditionContainers = container_data[2]

        ### creo il canvas relativo alla condition che sto aggiungendo ###
        conditionContainer = Canvas( lock_container, background = '#ffc04c', highlightthickness = 1, highlightbackground = "black", width = self.containerWidth, height = self.conditionHeight )
        lock_container.create_window( self.containerWidth/2, (100/100)*current_height, window = conditionContainer, anchor = 's' )
        semCanvas = Canvas( lock_container, background = '#ffc04c', width = 60, height = 17 )
        lock_container.create_window( self.containerWidth*(80/100), current_height-(45/100)*self.conditionHeight, window = semCanvas, anchor = 'n' )
        semCanvas.create_image( 15, 10, image = self.redSem, tag = "redSem", anchor = 'center' )
        semCanvas.create_image( 15, 10, image = self.greySem, tag = "greyRedSem", anchor = 'center' )
        semCanvas.create_text( 45, 12, text = "ONE" )

        semGreenCanvas = Canvas( lock_container, background = '#ffc04c', width = 60, height = 17 )
        lock_container.create_window( self.containerWidth*(20/100), current_height-(45/100)*self.conditionHeight, window = semGreenCanvas, anchor = 'n' )
        semGreenCanvas.create_image( 45, 10, image = self.greenSem, tag = "greenSem", anchor = 'center' )
        semGreenCanvas.create_image( 45, 10, image = self.greySem, tag = "greyGreenSem", anchor = 'center' )
        semGreenCanvas.create_text( 15, 12, text = "ALL" )


        conditionLabel = Label( conditionContainer, text = 'Condition '+condition.name )
        conditionLabel.place( relx = 0.5, rely = 0.70, anchor = 'c' )
        scroll = Scrollbar( conditionContainer, orient = HORIZONTAL, command = conditionContainer.xview )
        scroll.place( relx = 0, rely = 1, relwidth = 1, anchor = 'sw' )
        conditionContainer.configure( xscrollcommand = scroll.set )
        conditionData = ConditionContainer( conditionContainer, self.computerImage, self.conditionHeight, self.imageComputerHeight, self.imageComputerWidth, semCanvas, conditionLabel, semGreenCanvas )
        ### inserisco la condition nel container ###
        conditionContainers[ condition ] = conditionData
        self.conditions.append( conditionContainer )

    def update(self):
        self.primaryCanvas.configure(scrollregion=self.primaryCanvas.bbox("all"))
        self.inactiveCanvas.configure(scrollregion=self.inactiveCanvas.bbox("all")) 
        for key in self.modelData.getWaitContainerKeys():
            value = self.modelData.getWaitData(key)
            value.configure( scrollregion = value.bbox("all") )
        for container in self.conditions:
            container.configure(scrollregion=container.bbox("all"))
        self.window.after(50,self.updateCommand)

    def start(self):
        with self.startLock:
            for key in self.modelData.getLockContainerKeys():
                containerData=self.modelData.getLockData(key)
                container = containerData[7]
                currentOrient=containerData[4]

                relX = (20/100)*self.screen_width if currentOrient%2 == 0 else (80/100)*self.screen_width

                height = self.currentHeightLeftPosition if currentOrient%2 == 0 else self.currentHeightRightPosition
                self.primaryCanvas.create_window(relX,height,window=container,anchor='n')
                containerData[3]=height
                if(currentOrient%2 != 0):
                    self.currentHeightRightPosition+=containerData[6]+30
                else:
                    self.currentHeightLeftPosition+=containerData[6]+30
            self.window.after(50, self.updateCommand)
            self.started = True
            
            self.startCondition.notifyAll()
        self.window.mainloop()


    def initInstance(self, play, stop, next, popup, update, close):
        self.playButton.configure(command = play)
        self.stopButton.configure(command = stop)
        self.nextStepButton.configure(command = next)
        self.changeThreadButton.configure(command = popup)
        self.updateCommand = update
        self.window.protocol( 'WM_DELETE_WINDOW', close )

    pass


def setup() -> TkView:
    TkViewInstance = TkView()

    GeneralEventHandler().registerCallback('init', TkViewInstance.initInstance)
    GeneralEventHandler().registerCallback('play', TkViewInstance.play)
    GeneralEventHandler().registerCallback('stop', TkViewInstance.stop)
    GeneralEventHandler().registerCallback('start', TkViewInstance.start)

    ThreadEventHandler().registerCallback('add', TkViewInstance.newThread)

    LockEventHandler().registerCallback('add', TkViewInstance.newLock)

    ConditionEventHandler().registerCallback('add', TkViewInstance.newCondition)

    return TkViewInstance