import threading
from threadmonitor.utils import singleton
from tkinter import ttk
from tkinter import *
from typing import Any, Optional, Tuple
import threading
import time
from functools import partial
from threadmonitor.view.tk import InactiveContainer, WaitContainer, ConditionContainer 
from threadmonitor.view.tk import createAndEmplaceButton, getPhotoImage


class Controller:
    
    FINISH = False
    DESTRA = 1
    SINISTRA = 0
    INDEX_WAIT_CONTAINER = 1
    INDEX_LOCK_CONTAINER = 1
    isStopped = False
    
    def __init__(self):
        
        self.window = Tk()
        self.window.title( 'graphthreading' )
        self.stepLock = threading.Lock()
        self.stepCondition = threading.Condition(self.stepLock)

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_heigth = self.window.winfo_screenheight()
        self.pad = 3
        self.window.geometry( '{0}x{1}'.format( self.screen_width-self.pad, self.screen_heigth-self.pad ) )
        self.started = False
        self.step = 0
        self.startLock = threading.Lock()
        self.startCondition = threading.Condition( self.startLock )
        ### INIZIALIZZAZIONE LOGICA ###

        ### hashMap contenente come chiave il nome del lock, e come valore il relativo canvas ###
        self.lockContainer = {}
        
        ### In quale container è conenuto al momento il thread ###
        self.threadContainer = {}

        ### wait container associato a uno specifico lock ###
        self.waitContainer = {}

        ### Lista dei threads ###
        self.threads = []

        ### Lista dei thread inattivi ###
        self.inactiveThread = []

        ### Lista dei thread in wait su un determinato lock ###
        self.waitThread = {}

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

        #TODO: ?
        self.releasingLock = []
       
        ### Lista di tutti i container creati ###
        self.containers = []

        ### Contiene come chiave gli scroll, e come valore gli oggetti a cui sono attaccati ###
        self.scrolls = []

        #TODO: ?
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

        self.playButton = createAndEmplaceButton( self.primaryCanvas, 'play', self.play, relx = 0.93, rely = 0.02, relheight = 0.025 )
        self.stopButton = createAndEmplaceButton( self.primaryCanvas, 'pause', self.stop, relx = 0.93, rely = 0.045, relheight = 0.025 )
        self.nextStepButton = createAndEmplaceButton( self.primaryCanvas, 'next step', self.nextStep, relx = 0.93, rely = 0.070, relheight = 0.025 )
        self.nextStepButton.configure( state = 'disabled' )

        ### Inizializzazioni immagini ###
        self.imageComputerHeight = 32
        self.imageComputerWidth = 32
        self.computerImage = getPhotoImage( 'computer.png', (self.imageComputerHeight, self.imageComputerHeight), self.primaryCanvas )
        self.redSem = getPhotoImage( 'redSem.png', (15, 15), self.primaryCanvas )
        self.greenSem = getPhotoImage( 'greenSem.png', (15, 15), self.primaryCanvas )
        self.greySem = getPhotoImage( 'greySem.png', (15, 15), self.primaryCanvas )

        self.window.after( 50,self.update )
        self.window.protocol( 'WM_DELETE_WINDOW', self.__onclose )
        
        self.inactiveData = InactiveContainer( self.inactiveCanvas, self.computerImage )

    def play(self):
        with self.stepLock:
            self.stopButton.configure( state = 'normal' )
            self.nextStepButton.configure( state = 'disabled' )
            self.isStopped = False
            self.primaryCanvas.configure( background = '#A0A0A0' )
            for lock in self.lockContainer.keys():
                lock.playController.play()
            self.step = 0          
            self.stepCondition.notifyAll()
    
    #TODO: modifica di variabili senza sincronizzazione, è quello che vogliamo?
    def stop(self):
        self.playButton.configure( state = 'normal' )
        self.nextStepButton.configure( state = 'normal' )
        self.isStopped = True
        self.primaryCanvas.configure( background = '#696969' )
        for lock in self.lockContainer.keys():
            lock.playController.stop()
    
    def nextStep(self):
        with self.stepLock:
            self.step += 1
            self.stepCondition.notifyAll()

    def changeThreadName( self, label, textField, menu, button ):
        threads = {}
        for thread in self.threads:
            threads[ thread.getName() ] = thread
        threads[ label['text'] ].name = textField.get( '1.0', 'end-1c' )
        label.configure( text = 'Name modified!' )
        menu.delete(0, len(self.threads)-1 )
        for thread in self.threads:
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
        for thread in self.threads:
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

    def addThread( self, thread ):
        self.threads.append(thread)

    def setLockName( self, lock, name ):
        lock_data = self.lockContainer[lock]
        lock_label = lock_data[5]
        lock_label.configure( text = name )

    def addLock( self, lock ):
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
        self.waitContainer[ lock ]=waitContainer

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
        self.lockContainer[ lock ]=[lock_container, wait_data, conditionContainers, self.currentHeightPosition, self.currentOrientPosition%2, lockLabel, currentHeightCanvas, container ]
        
        ### aggiorno le variabili per il posizionamento ###
        self.currentOrientPosition += 1
        
    def addCondition( self, condition, lock ):
        ### prendo il container principale del lock a cui è associata la condition ###
        container_data = self.lockContainer[ lock ]
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

    def setConditionName( self, condition, lock, name ):
        lock_data = self.lockContainer[ lock ]
        conditionContainer = lock_data[2]
        conditionContainer[ condition ].setConditionLabel( name )

    def __moveFromInactiveToWait( self, thread, wait_container, height, orient, tag, lock, startTime ):
       
        if self.primaryCanvas.coords(tag)[1] <= height-(10/100)*self.containerHeight :
            
            self.primaryCanvas.move( f"image{ str(thread.ident) }", 0, 2 )
            self.primaryCanvas.move( tag, 0, 2 )
            self.primaryCanvas.after( 6, self.__moveFromInactiveToWait, thread, wait_container, height, orient, tag, lock, startTime )

        else:
            if orient == Controller.SINISTRA:
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
        if orient == Controller.SINISTRA:
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
        
        if orient == Controller.SINISTRA and  self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>(5/100)*self.primaryCanvas.winfo_width() and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,-1,0)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),-1,0)
            self.primaryCanvas.after(2,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
        elif orient == Controller.DESTRA and  self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<(95/100)*self.primaryCanvas.winfo_width() and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,1,0)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),1,0)
            self.primaryCanvas.after(2,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
        else:
            if self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
                self.primaryCanvas.move(tag,0,-3)
                self.primaryCanvas.move('inactiveimage'+str(thread.ident),0,-3)
                self.primaryCanvas.after(12,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
            else:
                if orient == Controller.DESTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>=((50/100)*self.screen_width)+((50/100)*self.inactiveWidth):# and (self.primaryCanvas.coords('inactiveimage'+thread)[0]<=(50/100)*self.screen_width):                    self.primaryCanvas.move(tag,1,0)
                    self.primaryCanvas.move('inactiveimage'+str(thread.ident),-2,0)
                    self.primaryCanvas.move(tag,-2,0)
                    self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,lock,container)
                elif orient == Controller.SINISTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<=((50/100)*self.screen_width)-((50/100)*self.inactiveWidth):# and self.primaryCanvas.coords('inactiveimage'+thread)[0]>=(50/100)*self.screen_width:                    self.primaryCanvas.move(tag,1,0)
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

    def setWaitThread( self, thread, lock ) -> float:
        
        if not self.started:
            self.startLock.acquire()
            while not self.started:
                self.startCondition.wait()
            self.startLock.release()
            time.sleep(0.05)
        
        container_data = self.lockContainer[lock]
        
        tag_param = "wait{0}{1}".format( str(thread.ident), str(lock.getId()) )
        val_x = int( self.primaryCanvas.winfo_width()/2 )
        anchor_param = 'n'
        
        self.primaryCanvas.create_text( val_x, (105/100)*self.imageComputerHeight, text = thread.getName(), tag = tag_param, anchor = anchor_param )
        self.primaryCanvas.create_image( val_x, 0, image = self.computerImage, tag = f"image{ str(thread.ident) }", anchor = anchor_param )
        
        wait_data = container_data[1]  
        height = container_data[3] + ((30/100)*self.containerHeight)
        orient = container_data[4]

        timeStart = time.time()
        self.__moveFromInactiveToWait( thread, wait_data, height, orient, tag_param, lock, timeStart )
        self.inactiveData.remove(thread)
        
        sleepTime = ( height + ( self.primaryCanvas.winfo_width()/2 ) - ( (30/100)*self.primaryCanvas.winfo_width() ) )/100 
        return sleepTime
    
    def setAcquireThread( self, thread, lock ):
        
        container_data = self.lockContainer[lock]
        
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
        container_data = self.lockContainer[lock]
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
        container_data = self.lockContainer[lock]
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
        container_data = self.lockContainer[lock]
        lock_container = container_data[0]
        height = container_data[3]+( (50/100)*self.containerHeight )
        orient = container_data[4]
        tagImage = 'acquireImage' + str(thread.ident)
        tagText = 'text' + str(thread.ident)
        
        tag = "release" + str(thread.ident)
        
        if orient == Controller.SINISTRA:
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
        container_data = self.lockContainer[lock]
        wait_data = container_data[1]
        wait_data.drawFutureAcquireThread(thread)

    def notifyLock(self,lock,condition,isAll):
        container_data = self.lockContainer[lock]
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
            container.after(400,self.__blinkCondition,container,startTime,not red)
        else:
            container.itemconfigure('greyRedSem',state='normal')

    def __blinkLock(self,container,currentState,lock):
        if lock in self.releasingLock:
            state = 'normal' if currentState else 'hidden'
            container.itemconfigure('greyRedSem',state=state) 
            container.after(500,self.__blinkLock,container, not currentState,lock)
        
    def update(self):
        self.primaryCanvas.configure(scrollregion=self.primaryCanvas.bbox("all"))
        self.inactiveCanvas.configure(scrollregion=self.inactiveCanvas.bbox("all")) 
        for key in self.waitContainer.keys():
            self.waitContainer[key].configure(scrollregion=self.waitContainer[key].bbox("all"))
        for container in self.conditions:
            container.configure(scrollregion=container.bbox("all"))
        self.window.after(50,self.update)
    
    def start(self):
        try:
            self.startLock.acquire()
            for key in self.lockContainer.keys():
                containerData=self.lockContainer[key]
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
            self.window.after(50,self.update)
            self.started = True
            
        except Exception as e:
            print(e)
        finally:
            self.startCondition.notifyAll()
            self.startLock.release()
            self.window.mainloop()

    def __onclose(self):
        self.window.destroy()
        for thread in self.threads:
            thread.exit()

    def run(self):
        with self.stepLock:
            if self.isStopped:
                while self.isStopped and self.step <= 0:
                    self.stepCondition.wait()
                self.step -= 1


@singleton
class SingletonController(Controller):
    pass
