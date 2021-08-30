# coding=utf-8

from functools import partial
import threading
from threadmonitor.controller import SingletonController
from threadmonitor.model.events import ConditionBroker, GeneralBroker, LockBroker, ThreadBroker
from tkinter import ttk
from tkinter import * 
from typing import Tuple
from PIL import ImageTk
import time
from threadmonitor.utils import getResourceFromName, overrides, singleton
import threadmonitor.model.logic as model
import pdb

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

    @overrides(AbstractTkContainer)
    def removeCondition(self, obj) -> bool:
        return obj in self.threads


class TkView:

    FINISH = False
    DESTRA = 1
    SINISTRA = 0
    INDEX_WAIT_CONTAINER = 1
    INDEX_LOCK_CONTAINER = 1
    isStopped = False

    def __init__(self):

        self.modelData = model.SingletonLogic()

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

        changeThreadButton = Button( self.inactiveCanvas, text = "Change thread name", command = self.createPopupThread )
        changeThreadButton.place( relx = 0.5, rely = 0, anchor = 'n' )

        self.inactiveScroll = ttk.Scrollbar( self.inactiveCanvas, orient = HORIZONTAL, command = self.inactiveCanvas.xview )
        self.inactiveScroll.place( relx = 0.5, rely = 0.93, width = 305, anchor = 'center' )

        self.inactiveCanvas.configure( xscrollcommand = self.inactiveScroll.set )
        #self.inactiveCanvas.pack(anchor='center',pady=10)
        self.background = getPhotoImage('background.png', (10000, self.screen_width), self.primaryCanvas)
        #self.primaryCanvas.create_image(0,0,image=self.background,anchor='n')

        self.primaryCanvas.create_window( self.screen_width/2, 0, window = self.inactiveCanvas, anchor = 'n' )

        self.playButton = createAndEmplaceButton( self.primaryCanvas, 'play', SingletonController().play, relx = 0.93, rely = 0.02, relheight = 0.025 )
        self.stopButton = createAndEmplaceButton( self.primaryCanvas, 'pause', SingletonController().stop, relx = 0.93, rely = 0.045, relheight = 0.025 )
        self.nextStepButton = createAndEmplaceButton( self.primaryCanvas, 'next step', SingletonController().next_step, relx = 0.93, rely = 0.070, relheight = 0.025 )
        self.nextStepButton.configure( state = 'disabled' )

        ### Inizializzazioni immagini ###
        self.imageComputerHeight = 32
        self.imageComputerWidth = 32
        self.computerImage = getPhotoImage( 'computer.png', (self.imageComputerHeight, self.imageComputerHeight), self.primaryCanvas )
        self.redSem = getPhotoImage( 'redSem.png', (15, 15), self.primaryCanvas )
        self.greenSem = getPhotoImage( 'greenSem.png', (15, 15), self.primaryCanvas )
        self.greySem = getPhotoImage( 'greySem.png', (15, 15), self.primaryCanvas )

        self.updateCmd = self.update

        self.window.update_idletasks()

        self.window.after( 50, self.updateCmd )
        self.window.protocol( 'WM_DELETE_WINDOW', self.destroy )
        
        self.inactiveData = InactiveContainer( self.inactiveCanvas, self.computerImage )

    def play(self):
        self.stopButton.configure( state = 'normal' )
        self.nextStepButton.configure( state = 'disabled' )
        self.primaryCanvas.configure( background = '#A0A0A0' )

    def stop(self):
        self.playButton.configure( state = 'normal' )
        self.nextStepButton.configure( state = 'normal' )
        self.primaryCanvas.configure( background = '#696969' )

    def newThread(self, thread) -> None:
        return

    def setConditionName( self, condition, lock, name ):
        lock_data = self.modelData.getLockData(lock)
        conditionContainer = lock_data[2]
        conditionContainer[ condition ].setConditionLabel( name )

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

        self.modelData.addLockData(lock, [lock_container, wait_data, conditionContainers, self.currentHeightPosition, self.currentOrientPosition%2, lockLabel, currentHeightCanvas, container])


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
        self.window.after(50, self.update)

    def start(self):
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
        self.window.after(50, self.updateCmd)

    def changeThreadName( self, label, textField, menu, button ):
        threads = {}
        for thread in self.modelData.getThreads():
            threads[ thread.getName() ] = thread
        threads[ label['text'] ].name = textField.get( '1.0', 'end-1c' )
        label.configure( text = 'Name modified!' )
        menu.delete(0, len(self.modelData.getThreads())-1 )
        for thread in self.modelData.getThreads():
            calling_data = partial( self.setLabel, label, thread.getName(), textField, button )
            menu.add_command( label = thread.getName(), command = calling_data )
        button.configure( state = 'disabled' )
        textField.configure( state = 'disabled' )
        
    def createPopupThread( self ):
        popup = Toplevel()
        popup.title( 'Change thread name' )
        popup.geometry( '400x200' )
        menu = Menu( popup )
        popup.config( menu = menu )
        threadBar = Menu( menu, tearoff = 0 )
        label=Label( popup, text = '' )
        label.place( rely = 0.25, relx = 0.5, anchor = 'n' )
        textField = Text( popup, state='disabled' )
        textField.place( relx = 0.5, rely = 0.40, relheight = 0.2, relwidth = 0.5, anchor = 'n' )      
        button = createAndEmplaceButton( popup, 'Change name', None, relx = 0.5, rely = 1, anchor = 's')
        button.configure( command = partial( self.changeThreadName, label, textField, threadBar, button ) )
        for thread in self.modelData.getThreads():
            calling_data = partial( self.setLabel, label, thread.getName(), textField, button )
            threadBar.add_command( label = thread.getName(), command = calling_data )
        menu.add_cascade( label = 'Select thread', menu = threadBar )       
        popup.mainloop()

    def setLabel( self, label, text, textField, button ):
        label.configure( text = text )
        textField.configure( state = "normal" )
        button.configure( state = "normal" )

    def createPopupLock( self, label ):
        popup = Toplevel()
        popup.title( label['text'] )
        popup.geometry( '400x100' )
        textField = Text( popup )
        textField.place( relx = 0, rely = 0, relheight = 0.5, relwidth = 1 )
        buttonCommand = lambda: ( label.configure( text = textField.get('1.0','end-1c') ) )
        createAndEmplaceButton( popup, 'Change name', buttonCommand, relx = 0.5, rely = 1, anchor = 's' )
        popup.mainloop()
    
    def setLockName( self, lock, name ):
        lock_data = self.modelData.getLockData(lock)
        lock_label = lock_data[5]
        lock_label.configure( text = name )

    def setAcquireThread( self, thread, lock ):
        container_data = self.modelData.getLockData(lock)
        
        lock_container = container_data[0]
        tag  = str( thread.ident )
        wait_container = container_data[1]
        
        wait_container.remove( thread )
        
        imageHeight = (25/100)*self.lockHeight
        imageWidth = (50/100)*self.containerWidth

        lock_container.create_image( imageWidth, imageHeight, tag = 'acquireImage'+tag, image = self.computerImage, anchor = 'n' )
        lock_container.create_text( imageWidth, imageHeight + ( 1.2*self.imageComputerHeight ), text = thread.getName(), tag = 'text' + tag, anchor = 'n', fill = 'green' )
        lock_container.itemconfigure( 'greyGreenSem', state = "normal" )
        lock_container.itemconfigure( 'greyRedSem', state = "hidden" )
        lock_container.itemconfigure( 'redSem', state = "normal" )
    
    def setAcquireThreadFromCondition( self, thread, lock, condition ):
        tag = str( thread.ident )
        container_data = self.modelData.getLockData(lock)
        conditionContainer = container_data[2]
        conditionData = conditionContainer[condition]
        conditionData.remove(thread)
        imageHeight = (25/100)*self.lockHeight
        imageWidth = (50/100)*self.containerWidth
        lock_container = container_data[0]
        lock_container.create_image( imageWidth, imageHeight, tag = 'acquireImage' + tag, image = self.computerImage, anchor = 'n' )
        lock_container.create_text( imageWidth, imageHeight + (1.2*self.imageComputerHeight), text = thread.getName(), tag = 'text' + tag, anchor = 'n', fill = 'green' )
        lock_container.itemconfigure( 'greyGreenSem', state = "normal" )
        lock_container.itemconfigure( 'greyRedSem', state = "hidden" )
        lock_container.itemconfigure( 'redSem', state = "normal" )

    def setThreadInCondition( self, thread, lock, condition ):
        container_data = self.modelData.getLockData(lock)
        conditionContainers = container_data[2]
        conditionData = conditionContainers[condition]
        conditionData.add(thread)
        lock_container = container_data[0]
        lock_container.delete( 'text' + str(thread.ident) )
        lock_container.delete( 'acquireImage' + str(thread.ident) )
        lock_container.itemconfigure( 'greyRedSem', state = 'normal' )         
        lock_container.itemconfigure( 'greyGreenSem', state = "hidden" )
        time.sleep(2)

    def setReleaseThread( self, thread, lock ):
        container_data = self.modelData.getLockData(lock)
        lock_container = container_data[0]
        height = container_data[3]+( (50/100)*self.containerHeight )
        orient = container_data[4]
        tagImage = 'acquireImage' + str(thread.ident)
        tagText = 'text' + str(thread.ident)
        
        tag = "release" + str(thread.ident)
        
        if orient == TkView.SINISTRA:
            width = (12/100)*self.primaryCanvas.winfo_width()
            self.primaryCanvas.create_image( width, height, tag = 'inactiveimage' + str(thread.ident), image = self.computerImage, anchor = 'n' )
            self.primaryCanvas.create_text( width, height + (1.2*self.imageComputerHeight), text = thread.getName(), tag = tag, anchor = 'n' )
        else:
            width = (88/100)*self.primaryCanvas.winfo_width()
            self.primaryCanvas.create_image( width, height, tag = 'inactiveimage' + str(thread.ident), image = self.computerImage, anchor = 'n' )
            self.primaryCanvas.create_text( width, height + (1.2*self.imageComputerHeight), text = thread.getName(), tag = tag, anchor = 'n' )
        self.__moveInLock( tagImage, tagText, orient, lock_container, lock, thread, tag, False )
        lock_container.itemconfigure( 'greyRedSem', state = "normal" )
        self.releasingLock.append(lock)
        lock_container.after( 500, self.__blinkLock, lock_container, True, lock )
        sleepTime = ( height + ( self.primaryCanvas.winfo_width()/2 ) - ( (30/100)*self.primaryCanvas.winfo_width() ) )/80
       
        return sleepTime
        
    def drawFutureLockThread( self, thread, lock ):
        container_data = self.modelData.getLockData(lock)
        wait_data = container_data[1]
        wait_data.drawFutureAcquireThread(thread)

    def notifyLock(self,lock,condition,isAll):
        container_data = self.modelData.getLockData(lock)
        conditionContainer = container_data[2]
        conditionData = conditionContainer[condition]
        startTime = time.time()
        red = True
        grey = "greyRedSem" if not isAll else "greyGreenSem"
        conditionData.blinkCondition(startTime,red,grey)
    
    def __blinkCondition(self,container,startTime,red):
        currentTime = time.time()
        if currentTime<=startTime+7:
            state = "hidden" if red else "normal"
            container.itemconfigure('greyRedSem',state=state)
        else:
            container.itemconfigure('greyRedSem',state='normal')

    def __blinkLock(self,container,currentState,lock):
        if lock in self.releasingLock:
            state = 'normal' if currentState else 'hidden'
            container.itemconfigure('greyRedSem',state=state) 

    def setWaitThread( self, thread, lock ) -> float:

        container_data = self.modelData.getLockData(lock)

        tag_param = "wait{0}{1}".format( str(thread.ident), str(lock.getId()) )
        print(f'{self} parameter tag_param: {tag_param}')
        val_x = int( self.primaryCanvas.winfo_width()/2 )
        print(f'{self} parameter val_x: {val_x}')
        anchor_param = 'n'

        try:
            #pdb.set_trace()
            self.primaryCanvas.create_text( val_x, (105/100)*self.imageComputerHeight, text = thread.getName(), tag = tag_param, anchor = anchor_param )
            #pdb.set_trace()
            self.primaryCanvas.create_image( val_x, 0, image = self.computerImage, tag = f"image{ str(thread.ident) }", anchor = anchor_param )
        except Exception as e:
            print(e)
        print(f'{self} canvas updated')

        wait_data = container_data[1]  
        height = container_data[3] + ((30/100)*self.containerHeight)
        orient = container_data[4]

        timeStart = time.time()
        self.__moveFromInactiveToWait( thread, wait_data, height, orient, tag_param, lock, timeStart )
        self.inactiveData.remove(thread)
            
        sleepTime = ( height + ( self.primaryCanvas.winfo_width()/2 ) - ( (30/100)*self.primaryCanvas.winfo_width() ) )/100 
        return sleepTime

    def __moveFromInactiveToWait( self, thread, wait_container, height, orient, tag, lock, startTime ):

        if self.primaryCanvas.coords(tag)[1] <= height-(10/100)*self.containerHeight :
            
            self.primaryCanvas.move( f"image{ str(thread.ident) }", 0, 2 )
            self.primaryCanvas.move( tag, 0, 2 )
            self.primaryCanvas.after( 6, self.__moveFromInactiveToWait, thread, wait_container, height, orient, tag, lock, startTime )

        else:
            if orient == TkView.SINISTRA:
                if self.primaryCanvas.coords(tag)[0] >= ( (30/100)*self.primaryCanvas.winfo_width() ):
                    
                    self.primaryCanvas.move( tag, -2, 0 )
                    self.primaryCanvas.move( f"image{ str(thread.ident) }", -2, 0 )
                    self.primaryCanvas.after( 10, self.__moveFromInactiveToWait, thread, wait_container, height, orient, tag, lock, startTime )
                
                else:
                    wait_container.add( thread, lock )
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete( f"image{ str(thread.ident) }" )
            
            else:
                if self.primaryCanvas.coords(tag)[0] <= ( (70/100)*self.primaryCanvas.winfo_width() ):
            
                    self.primaryCanvas.move( tag, 2, 0 )
                    self.primaryCanvas.move( f"image{ str(thread.ident) }", 2, 0 )
                    self.primaryCanvas.after( 10, self.__moveFromInactiveToWait, thread, wait_container, height, orient, tag, lock, startTime )
            
                else:
                    wait_container.add( thread, lock )
                    lock.canAcquire = True
                    self.primaryCanvas.delete( tag )
                    self.primaryCanvas.delete( f"image{ str(thread.ident) }" )

    
    def __moveInLock(self,tagImage, tagText,orient,container,lock,thread,tag,alreadyCalled):
        if orient == TkView.SINISTRA:
            if container.coords(tagImage)[0]>0:
                if container.coords(tagImage)[0]<16:
                    if not alreadyCalled:
                        self.__moveFromLockToInactive(tag,thread,orient,lock,container)
                        alreadyCalled = True

                container.move(tagImage,-1,0)
                container.move(tagText,-1,0)
                container.after(2,self.__moveInLock,tagImage, tagText, orient,container,lock,thread,tag,alreadyCalled)
            else:
                container.delete(tagImage)
                container.delete(tagText)
        else:
            if container.coords(tagImage)[0]<self.containerWidth:
                if container.coords(tagImage)[0]>self.containerWidth-32:
                    if not alreadyCalled:
                        self.__moveFromLockToInactive(tag,thread,orient,lock,container)
                        alreadyCalled = True

                container.move(tagImage,1,0)
                container.move(tagText,1,0)
                container.after(4,self.__moveInLock,tagImage, tagText, orient,container,lock,thread,tag,alreadyCalled)
            else:
                container.delete(tagImage)
                container.delete(tagText)
                

    def __moveFromLockToInactive(self,tag,thread,orient,lock,container):
        
        if orient == TkView.SINISTRA and  self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>(5/100)*self.primaryCanvas.winfo_width() and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,-1,0)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),-1,0)
            self.primaryCanvas.after(2,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
        elif orient == TkView.DESTRA and  self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<(95/100)*self.primaryCanvas.winfo_width() and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,1,0)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),1,0)
            self.primaryCanvas.after(2,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
        else:
            if self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
                self.primaryCanvas.move(tag,0,-3)
                self.primaryCanvas.move('inactiveimage'+str(thread.ident),0,-3)
                self.primaryCanvas.after(12,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
            else:
                if orient == TkView.DESTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>=((50/100)*self.screen_width)+((50/100)*self.inactiveWidth):# and (self.primaryCanvas.coords('inactiveimage'+thread)[0]<=(50/100)*self.screen_width):                    self.primaryCanvas.move(tag,1,0)
                    self.primaryCanvas.move('inactiveimage'+str(thread.ident),-2,0)
                    self.primaryCanvas.move(tag,-2,0)
                    self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
                elif orient == TkView.SINISTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<=((50/100)*self.screen_width)-((50/100)*self.inactiveWidth):# and self.primaryCanvas.coords('inactiveimage'+thread)[0]>=(50/100)*self.screen_width:                    self.primaryCanvas.move(tag,1,0)
                    self.primaryCanvas.move('inactiveimage'+str(thread.ident),2,0)
                    self.primaryCanvas.move(tag,2,0)
                    self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
                else:
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('inactiveimage'+str(thread.ident))
                    self.inactiveData.add(thread,lock)
                    self.releasingLock.remove(lock)
                    container.itemconfigure('greyRedSem',state='normal')         
                    container.itemconfigure('greyGreenSem',state="hidden")

    def mainloop(self):
        self.window.mainloop()

    def destroy(self):
        self.window.destroy()
        for thread in self.modelData.getThreads():
            thread.exit()


@singleton
class SingletonTkView(TkView):
    pass

def setup() -> TkView:

    print(f'attempiting to set up callbacks')

    GeneralBroker().registerCallback('start', SingletonTkView().start)
    GeneralBroker().registerCallback('play', SingletonTkView().play)
    GeneralBroker().registerCallback('stop', SingletonTkView().stop)
    GeneralBroker().registerCallback('mainloop', SingletonTkView().mainloop)

    ThreadBroker().registerCallback('add', SingletonTkView().newThread)

    LockBroker().registerCallback('add', SingletonTkView().newLock)
    LockBroker().registerCallback('setWaitThread', SingletonTkView().setWaitThread)
    LockBroker().registerCallback('drawFutureLockThread', SingletonTkView().drawFutureLockThread)
    LockBroker().registerCallback('setAcquireThread', SingletonTkView().setAcquireThread)
    LockBroker().registerCallback('setAcquireThreadFromCondition', SingletonTkView().setAcquireThreadFromCondition)
    LockBroker().registerCallback('setReleaseThread', SingletonTkView().setReleaseThread)
    LockBroker().registerCallback('setThreadInCondition', SingletonTkView().setThreadInCondition)
    LockBroker().registerCallback('setLockName', SingletonTkView().setLockName)

    ConditionBroker().registerCallback('add', SingletonTkView().newCondition)
    ConditionBroker().registerCallback('notifyLock', SingletonTkView().notifyLock)
    ConditionBroker().registerCallback('setConditionName', SingletonTkView().setConditionName)

    print('callbacks set')

    return SingletonTkView()