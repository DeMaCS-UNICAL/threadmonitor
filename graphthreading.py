from threading import Lock,Condition
from threading import current_thread
from time import sleep
from tkinter import ttk
from tkinter import *
import tkinter
from threading import Lock,Thread
from PIL import ImageTk
import os
import threading
import time
from functools import partial





class _InactiveContainer:
    def __init__(self,inactiveContainer,image):
        self.container = inactiveContainer
        self.lock = Lock()
        self.inactiveThreads = []
        self.currentWidth = 0
        self.image = image

    def addThreadInactive(self,thread,lock):
        with self.lock:
            self.inactiveThreads.append(thread)
            ##print("Add thread inactive ",thread_name)
            self.drawNewThread(thread,lock)

    def removeThreadInactive(self,threadObject):
        with self.lock:
            if threadObject in self.inactiveThreads:
                for thread in self.inactiveThreads:
                    self.container.delete('image'+str(thread.ident))
                    self.container.delete('text'+str(thread.ident))
                self.inactiveThreads.remove(threadObject)
                ##print(self.inactiveThreads)
                self.redrawThread()
    
    def redrawThread(self):
        currentWidth = 0
        

        for thread in self.inactiveThreads:
            tag=str(thread.ident)
            self.container.create_image(currentWidth,30,image=self.image,tag='image'+tag,anchor='n')
            self.container.create_text(currentWidth,100,text=thread.getName(),tag='text'+tag,anchor="n")
            currentWidth+=100
        self.currentWidth=currentWidth
    
    def drawNewThread(self,thread,lock):
        lock.releaseLock.acquire()
        tag = str(thread.ident)
        self.container.create_image(self.currentWidth,30,image=self.image,tag='image'+tag,anchor='n')
        self.container.create_text(self.currentWidth,100,text=thread.getName(),tag='text'+tag,anchor="n")
        self.currentWidth +=100
        lock.releaseCondition.notify_all()
        lock.isReleased=True
        #print('release lock draw ',lock.getId(), current_thread().getName())
        lock.releaseLock.release()



class _WaitContainer:
    def __init__(self,wait_container,image):
        self.container = wait_container
        self.lock = Lock()
        self.waitThreads = []
        self.currentHeight = 0
        self.image = image
    
    def addThreadInWait(self,thread,lock):
        with self.lock:
            self.waitThreads.append(thread)
            ##print("Add thread ",thread_name)
            self.drawNewThread(thread)
            lock.canAquire=True
            ##print('acquired')

    def removeThreadInWait(self,threadObject):
        with self.lock:
            ##print(self.waitThreads)
            for thread in self.waitThreads:
                tag = str(thread.ident)
                self.container.delete('text'+tag)
                
                self.container.delete('image'+str(thread.ident))

            self.waitThreads.remove(threadObject)
            self.redrawThread()
    
    def redrawThread(self):
        currentHeight = 0
        

        for thread in self.waitThreads:
            tag=str(thread.ident)
            self.container.create_image(int(self.container.winfo_width()/2),currentHeight,image=self.image,tag='image'+tag,anchor='n')
            currentHeight+=70
            self.container.create_text(int(self.container.winfo_width()/2),currentHeight,text=thread.getName(),tag='text'+tag,anchor="n")
            currentHeight+=20
        self.currentHeight=currentHeight
    
    def drawNewThread(self,thread):
        tag = str(thread.ident)
        self.container.create_image(int(self.container.winfo_width()/2),self.currentHeight,image=self.image,tag='image'+tag,anchor='n')
        self.currentHeight+=70
        self.container.create_text(int(self.container.winfo_width()/2),self.currentHeight,text=thread.getName(),tag='text'+tag,anchor="n")
        self.currentHeight +=20

    def drawFutureAcquireThread(self):
        if len(self.waitThreads)>0:
            #self.container.itemconfigure('text'+str(self.waitThreads[0].ident),fill='#cd5b45')
            #TODO
            pass

class _modifyLockNameWindow:
    def __init__(self,lock):
        pass
class Controller:
    FINISH=False
    DESTRA = 1
    SINISTRA = 0
    INDEX_WAIT_CONTAINER = 1
    INDEX_LOCK_CONTAINER = 1

    
    def __init__(self):
        
        self.window=Tk()


        self.screen_width=self.window.winfo_screenwidth()
        self.screen_heigth=self.window.winfo_screenheight()
        self.pad = 3
        self.window.geometry('{0}x{1}'.format(self.screen_width-self.pad,self.screen_heigth-self.pad))
        self.started = False
        ### INIZIALIZZAZIONE LOGICA ###

        ### hashMap contenente come chiave il nome del lock, e come valore il relativo canvas ###
        self.lockContainer={}
        
        ### In quale container è conenuto al momento il thread ###
        self.threadContainer = {}

        ### wait container associato a uno specifico lock ###
        self.waitContainer = {}

        ### Lista dei threads ###
        self.threads = []

        ### Lista dei thread inattivi ###
        self.inactiveThread=[]

        ### Lista dei thread in wait su un determinato lock ###
        self.waitThread = {}

        ### PUNTI DI PARTENZA DEI CONTAINERS ###
        self.currentOrientPosition = 0
        self.currentHeightPosition = 200
        self.containerWidth = self.screen_width/5
        self.containerHeight = self.screen_heigth/2
        self.releasingLock = []
        '''
        ### FINE INIZIALIZZAZIONE LOGICA ###


        ### INIZIO COSTRUZIONE FINESTRA STATICA ###
        

        ### Inizializzazione inactive Frame ###
        self.inactiveFrame=Frame(self.window,background='#DACFCF')
        self.inactiveFrame.pack(fill=BOTH)

        ### Inizializzazione inactive Canvas ###
        self.inactiveCanvas=Canvas(self.inactiveFrame,background='red',highlightthickness=1, highlightbackground="black",height=100,width=300)
        self.inactiveCanvas.pack(anchor='center',pady=10)

        ### Inizializzazione master Canvas ###
        ### Inizializzazione primo layer ###
        ### In questo canvas si muoveranno i lock che devono instradarsi verso i contenitori ###
        self.masterCanvas=Canvas(self.window,background='gray',highlightthickness=0, highlightbackground="grey")
        self.masterCanvas.pack(fill=BOTH,expand=True)

       
        ### Creazione dello spazio che conterrà tutti i lock ###
        self.frame=Frame(self.masterCanvas,width=self.screen_width,background='white')
        self.frame.place(y=1000)
        self.masterCanvas.create_window(self.screen_width, self.screen_heigth, window=self.frame, anchor='nw')
        self.primaryCanvas=Canvas(self.frame,background='black',highlightthickness=1, highlightbackground="black",height=10000,width=self.screen_width)
        self.primaryCanvas.pack(anchor = 'n')
        '''
        '''
        self.inactiveFrame=Frame(self.window,background='#DACFCF')
        self.inactiveFrame.pack(fill=BOTH)
        self.inactiveCanvas=Canvas(self.inactiveFrame,background='red',highlightthickness=1, highlightbackground="black",height=100,width=300)
        self.inactiveCanvas.pack(anchor='center',pady=10)
        
        self.masterCanvas=Canvas(self.window,background='black',highlightthickness=0, highlightbackground="black")

        self.masterCanvas.pack(fill=BOTH,expand=True)

        self.frame=Frame(self.masterCanvas,width=self.screen_width,background='white')
        self.frame.place(y=1000)
        self.masterCanvas.create_window(10000, self.screen_heigth, window=self.frame, anchor='nw')

        
        

        ### Inizializzazioni scroll ###
        self.inactiveScroll = Scrollbar(self.inactiveCanvas,orient=HORIZONTAL,command=self.inactiveCanvas.xview)
        self.inactiveScroll.place(relx=0.5,rely=0.9,relwidth=1,anchor='center')
        self.inactiveCanvas.configure(xscrollcommand=self.inactiveScroll.set)

        

        
        ### FINE COSTRUZIONE FINESTRA STATICA ###


        
        ###print(self.primaryCanvas.winfo_screenmmwidth())
        #self.image=self.masterCanvas.create_image(int(self.window.winfo_screenmmwidth()/2),200,image=self.computerImage,anchor='center',tags='pc',state=tkinter.NORMAL)
        '''
        ### Lista di tutti i container creati ###
        self.containers = []

        ### Contiene come chiave gli scroll, e come valore gli oggetti a cui sono attaccati ###
        self.scrolls = []
        '''
        self.frame.configure(height=700*4)
        self.yscroll = Scrollbar(self.masterCanvas, orient=VERTICAL)
        self.yscroll.pack(side=RIGHT,fill=Y)
        '''
        ### Inizializzazione inactive Frame ###
        
        #self.inactiveFrame=Frame(self.window,background='#ff1a1a')
        #self.inactiveFrame.pack(fill=BOTH)
        

        ### Inizializzazione primaryCanvas ###

        self.frame=Frame(self.window,width=self.screen_width,height = self.screen_heigth,background='grey')
        self.frame.pack(fill=BOTH,expand=True)
        self.primaryCanvas=Canvas(self.frame,background='#dbdbdb',highlightthickness=0, highlightbackground="black",height=10000,width=self.screen_width)
        self.window.update_idletasks()
        self.yscroll = Scrollbar(self.frame, orient=VERTICAL)
        self.yscroll['command']= self.primaryCanvas.yview
        self.yscroll.pack(side=RIGHT,fill=Y)
        self.primaryCanvas['yscrollcommand']= self.yscroll.set
        self.primaryCanvas.pack(fill=BOTH,expand=True)

        self.inactiveCanvas=Canvas(self.primaryCanvas,background='white',highlightthickness=1, highlightbackground="black",height=150,width=500)
        changeThreadButton = Button(self.inactiveCanvas,text = "Change thread name", command=self.createPopupThread)
        changeThreadButton.place(relx=0.5,rely=0,anchor='n')
        self.inactiveScroll = ttk.Scrollbar(self.inactiveCanvas,orient=HORIZONTAL,command=self.inactiveCanvas.xview)
        self.inactiveScroll.place(relx=0.5,rely=0.93,width=305,anchor='center')
        self.inactiveCanvas.configure(xscrollcommand=self.inactiveScroll.set)
        #self.inactiveCanvas.pack(anchor='center',pady=10)
        self.background = ImageTk.Image.open('resource/background.jpg')
        self.background = self.background.resize((10000,self.screen_width))
        self.background = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.background)
        #self.primaryCanvas.create_image(0,0,image=self.background,anchor='n')

        self.primaryCanvas.create_window(self.screen_width/2,0,window=self.inactiveCanvas,anchor='n')

        self.playButton = Button(self.primaryCanvas,text='play',command=self.play)
        self.stopButton = Button(self.primaryCanvas,text='stop',command=self.stop)

        self.playButton.place(relx=0.93,rely=0.02)
        self.stopButton.place(relx=0.93,rely=0.08)
        ### Inizializzazioni immagini ###
        self.imageComputerHeight = int((15/100)*self.containerHeight)
        self.computerImage = ImageTk.Image.open('resource/computer.png')
        self.computerImage = self.computerImage.resize((int((25/100)*self.containerWidth),int((15/100)*self.containerHeight)))
        self.computerImage = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.computerImage)

        self.redSem = ImageTk.Image.open('resource/redSem.png')
        self.redSem = self.redSem.resize((20,20))
        self.redSem = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.redSem)

        self.greenSem = ImageTk.Image.open('resource/greenSem.png')
        self.greenSem = self.greenSem.resize((20,20))
        self.greenSem = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.greenSem)

        self.greySem = ImageTk.Image.open('resource/greySem.png')
        self.greySem = self.greySem.resize((20,20))
        self.greySem = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.greySem)
       
        self.window.after(50,self.update)
        self.window.protocol('WM_DELETE_WINDOW',self.__onclose)

        self.inactiveData = _InactiveContainer(self.inactiveCanvas,self.computerImage)

    def play(self):
        self.primaryCanvas.configure(background='#dbdbdb')
        for lock in self.lockContainer.keys():
            lock.playController.play()
    
    def stop(self):
        self.primaryCanvas.configure(background='#696969')
        for lock in self.lockContainer.keys():
            lock.playController.stop()
    def changeThreadName(self,label,textField,menu,button):
        threads={}
        for thread in self.threads:
            threads[thread.getName()]=thread
        threads[label['text']].name=textField.get('1.0','end-1c')
        label.configure(text='Name modified!')
        menu.delete(0,len(self.threads)-1)
        for thread in self.threads:
            calling_data = partial(self.setLabel,label,thread.getName(),textField,button)
            menu.add_command(label=thread.getName(),command= calling_data)
        button.configure(state='disabled')
        textField.configure(state='disabled')

        
    def createPopupThread(self):
        popup = Toplevel()
        popup.title('Change thread name')
        popup.geometry('400x200')
        menu = Menu(popup)
        popup.config(menu=menu)
        threadBar = Menu(menu,tearoff=0)
        label=Label(popup,text='')
        label.place(rely=0.25,relx=0.5,anchor='n')
        textField = Text(popup,state='disabled')
        textField.place(relx=0.5,rely=0.40,relheight=0.2,relwidth=0.5,anchor='n')
        changeThreadNameData=partial(self.changeThreadName,label,textField,threadBar)
        
        button = Button(popup,text='Change name')
        changeThreadNameData=partial(self.changeThreadName,label,textField,threadBar,button)
        button.configure(command= changeThreadNameData)
        button.place(relx=0.5,rely=1,anchor='s')
        for thread in self.threads:
            calling_data = partial(self.setLabel,label,thread.getName(),textField,button)
            threadBar.add_command(label=thread.getName(),command= calling_data)
        menu.add_cascade(label='Select thread',menu=threadBar)
        
        popup.mainloop()

    def setLabel(self,label,text,textField,button):
        label.configure(text=text)
        textField.configure(state="normal")
        button.configure(state="normal")
    def createPopupLock(self,label):
        popup = Toplevel()
        popup.title(label['text'])
        popup.geometry('400x100')
        textField = Text(popup)
        textField.place(relx=0,rely=0,relheight=0.5,relwidth=1)
        button = Button(popup,text='Change name',command= lambda: (label.configure(text=textField.get('1.0','end-1c'))))
        button.place(relx=0.5,rely=1,anchor='s')
        popup.mainloop()

    def addThread(self,thread):
        self.threads.append(thread)
        #self.inactiveData.addThreadInactive(thread.getName())

    def addLock(self,lock):
        ### creo il container e lo aggiungo alla lista di container ###
        
        container=Canvas(self.primaryCanvas,background='white',highlightthickness=1, highlightbackground="black",height=self.containerHeight,width=self.containerWidth)
        
        
        self.containers.append(container)
        relX = (20/100)*self.screen_width if self.currentOrientPosition%2 == 0 else (80/100)*self.screen_width
        self.primaryCanvas.create_window(relX,self.currentHeightPosition,window=container,anchor='n')#container.place(relx=relX,y=self.currentHeightPosition,anchor='n')

        lockLabel = Label(container,text = 'Lock '+str(lock.getId()))
        lockLabel.place(relx=0.5,rely=0.70,anchor='center')

        changeLockLabelData = partial(self.createPopupLock,lockLabel)
        button = Button(container,text='Change lock name',command = changeLockLabelData)
        button.place(relx=0.5,rely=0.25,anchor='n')
        ### creo il container per i thread in wait ###
        waitContainer= Canvas(container,background='#fff7dc',highlightthickness=1, highlightbackground="black",width=self.containerWidth,height=int(self.containerHeight*(25/100)))
        container.create_window(self.containerWidth/2,(0/100)*self.containerHeight,window=waitContainer,anchor='n')#.place(relx=0.5,anchor='center',rely=0.25, relheight=0.50,relwidth=1)
        waitLabel = Label(waitContainer,text='Wait threads')
        waitLabel.place(relx=0,rely=0,anchor='nw')
        self.waitContainer[lock]=waitContainer

        container.create_image(self.containerWidth*(90/100),self.containerHeight*(50/100),image=self.redSem, tag="redSem",state="hidden")
        container.create_image(self.containerWidth*(90/100),self.containerHeight*(50/100),image=self.greySem, tag="greyRedSem")

        container.create_image(self.containerWidth*(90/100),self.containerHeight*(60/100),image=self.greenSem, tag="greenSem")
        container.create_image(self.containerWidth*(90/100),self.containerHeight*(60/100),image=self.greySem, tag="greyGreenSem",state="hidden")


        #container.itemconfigure("redSem",state="hidden")
        
        
        ### creo il relativo scroll ###
        scroll = Scrollbar(waitContainer,orient=VERTICAL,command=waitContainer.yview)
        scroll.place(relx=1,rely=0.5,relheight=1,anchor='e')
        waitContainer.configure(yscrollcommand=scroll.set)
        self.scrolls.append(scroll)
        
        wait_data = _WaitContainer(waitContainer,self.computerImage)

        conditionContainer = Canvas(container,background='#ffc04c',highlightthickness=1, highlightbackground="black",width=self.containerWidth,height=int(self.containerHeight*(25/100)))
        container.create_window(self.containerWidth/2,(75/100)*self.containerHeight,window=conditionContainer,anchor='n')#.place(relx=0.5,anchor='center',rely=0.25, relheight=0.50,relwidth=1)
        conditionContainer.create_image(self.containerWidth*(90/100),(20/100)*(25/100)*self.containerHeight,image=self.redSem, tag="redSem")
        conditionContainer.create_image(self.containerWidth*(90/100),(20/100)*(25/100)*self.containerHeight,image=self.greySem, tag="greyRedSem")
        conditionLabel = Label(conditionContainer,text='Condition threads')
        conditionLabel.place(relx=0,rely=0,anchor='nw')
        ### associo al lock il relativo container ###
        self.lockContainer[lock]=[container,wait_data,conditionContainer,self.currentHeightPosition,self.currentOrientPosition%2,lockLabel]
        
        ### aggiorno le variabili per il posizionamento ###
        self.currentOrientPosition+=1
        if(self.currentOrientPosition%2 == 0):
            self.currentHeightPosition+=self.containerHeight+30
        
        
        
    def __moveFromInactiveToWait(self,thread,wait_container,height,orient,tag,lock,startTime):
       
        if self.primaryCanvas.coords(tag)[1]<=height-(10/100)*self.containerHeight:
            self.primaryCanvas.move('image'+str(thread.ident),0,2)
            self.primaryCanvas.move(tag,0,2)
            self.primaryCanvas.after(6,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)

                
        else:
            if orient == Controller.SINISTRA:
                if self.primaryCanvas.coords(tag)[0]>=((20/100)*self.primaryCanvas.winfo_width()):
                    self.primaryCanvas.move(tag,-2,0)
                    self.primaryCanvas.move('image'+str(thread.ident),-2,0)
                    self.primaryCanvas.after(10,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)
                else:
                    #wait_container.create_text(int(wait_container.winfo_width()/2),0,text=thread,tag=tag,anchor="n")
                    endTime = time.time()
                    ##print('Time is: ',endTime-startTime, '\nHeight is: ',height,'\nWidth is: ',self.primaryCanvas.winfo_width(),'\nCoords of thread is: ',self.primaryCanvas.coords(tag))
                    wait_container.addThreadInWait(thread,lock)
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('image'+str(thread.ident))


            else:
                if self.primaryCanvas.coords(tag)[0]<=((80/100)*self.primaryCanvas.winfo_width()):
                    self.primaryCanvas.move(tag,2,0)
                    self.primaryCanvas.move('image'+str(thread.ident),2,0)
                    self.primaryCanvas.after(10,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)
                else:
                    #wait_container.create_text(int(wait_container.winfo_width()/2),0,text=thread,tag=tag,anchor="n")
                    endTime = time.time()
                    ###print('Time is: ',endTime-startTime, '\nHeight is: ',height,'\nWidth is: ',self.primaryCanvas.winfo_width())
                    wait_container.addThreadInWait(thread,lock)
                    lock.canAcquire=True
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('image'+str(thread.ident))

    def __moveFromLockToInactive(self,tag,thread,orient,startTime,lock,wait_data,container):
        
        if self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[1]>0:
            self.primaryCanvas.move(tag,0,-3)
            self.primaryCanvas.move('inactiveimage'+str(thread.ident),0,-3)
            wait_data.drawFutureAcquireThread()
            self.primaryCanvas.after(12,self.__moveFromLockToInactive,tag,thread,orient,startTime,lock,wait_data,container)
        else:
            if orient == Controller.DESTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]>=((50/100)*self.screen_width):# and (self.primaryCanvas.coords('inactiveimage'+thread)[0]<=(50/100)*self.screen_width):                    self.primaryCanvas.move(tag,1,0)
                self.primaryCanvas.move('inactiveimage'+str(thread.ident),-2,0)
                self.primaryCanvas.move(tag,-2,0)
                wait_data.drawFutureAcquireThread()
                self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,startTime,lock,wait_data,container)
            elif orient == Controller.SINISTRA and self.primaryCanvas.coords('inactiveimage'+str(thread.ident))[0]<=((50/100)*self.screen_width):# and self.primaryCanvas.coords('inactiveimage'+thread)[0]>=(50/100)*self.screen_width:                    self.primaryCanvas.move(tag,1,0)
                self.primaryCanvas.move('inactiveimage'+str(thread.ident),2,0)
                self.primaryCanvas.move(tag,2,0)
                wait_data.drawFutureAcquireThread()
                self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,startTime,lock,wait_data,container)
            else:
                self.primaryCanvas.delete(tag)
                self.primaryCanvas.delete('inactiveimage'+str(thread.ident))
                self.inactiveData.addThreadInactive(thread,lock)
                self.releasingLock.remove(lock)
                container.itemconfigure('greyRedSem',state='normal')         
                container.itemconfigure('greyGreenSem',state="hidden")
                endTime = time.time()
                ##print('Release time is: ',endTime-startTime)


    def setWaitThread(self,thread,lock):
        
        container_data = self.lockContainer[lock]
        

        wait_data = container_data[1]
        
        #if wait_container
        height = container_data[3]+((30/100)*self.containerHeight)
        orient = container_data[4]
        tag="wait"+str(thread.ident)+str(lock.getId())
        
        self.primaryCanvas.create_text(int(self.primaryCanvas.winfo_width()/2),(105/100)*self.imageComputerHeight,text=thread.getName(),tag=tag,anchor="n")
        self.primaryCanvas.create_image(int(self.primaryCanvas.winfo_width()/2),0,image=self.computerImage,tag='image'+str(thread.ident),anchor='n')
        timeStart = time.time()
        self.__moveFromInactiveToWait(thread,wait_data,height,orient,tag,lock,timeStart)
        self.inactiveData.removeThreadInactive(thread)

        sleepTime = (height+(self.primaryCanvas.winfo_width()/2)-((30/100)*self.primaryCanvas.winfo_width()))/100 
        return sleepTime
    
    def setAcquireThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        ##print('Acquire lock from ',lock.getId())
        lock_container = container_data[0]
        tag=str(thread.ident)
        
        wait_container = container_data[1]
        wait_container.removeThreadInWait(thread)
        lock_container.create_image((50/100)*self.containerWidth,(40/100)*self.containerHeight,tag = 'acquireImage'+tag,image=self.computerImage,anchor='n')
        lock_container.create_text((50/100)*self.containerWidth,(55/100)*self.containerHeight,text=thread.getName(),tag='text'+tag,anchor='n',fill='green')
        lock_container.itemconfigure('greyGreenSem',state="normal")
        lock_container.itemconfigure('greyRedSem',state="hidden")
        lock_container.itemconfigure('redSem',state="normal")
    
    def setAcquireThreadFromCondition(self,thread,lock):
        tag=str(thread.ident)
        container_data = self.lockContainer[lock]
        conditionContainer =container_data[2]
        conditionContainer.delete('image'+tag)
        conditionContainer.delete('text'+tag)

        lock_container = container_data[0]
        lock_container.create_image((50/100)*self.containerWidth,(40/100)*self.containerHeight,tag = 'acquireImage'+tag,image=self.computerImage,anchor='n')
        lock_container.create_text((50/100)*self.containerWidth,(55/100)*self.containerHeight,text=thread.getName(),tag='text'+tag,anchor='n',fill='green')
        lock_container.itemconfigure('greyGreenSem',state="normal")
        lock_container.itemconfigure('greyRedSem',state="hidden")
        lock_container.itemconfigure('redSem',state="normal")
    

    def setThreadInCondition(self,thread,lock):
        tag=str(thread.ident)
        container_data = self.lockContainer[lock]
        conditionContainer =container_data[2]
        imageHeight = (10/100)*(25/100)*self.containerHeight
        conditionContainer.create_image(30,imageHeight,image=self.computerImage,tag='image'+tag,anchor='n')
        conditionContainer.create_text(30,imageHeight+(120/100)*self.imageComputerHeight,text=thread.getName(),tag='text'+tag,anchor="n")    

        lock_container=container_data[0]
        lock_container.delete('text'+str(thread.ident))
        lock_container.delete('acquireImage'+str(thread.ident))

    def setReleaseThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        lock_container=container_data[0]
        lock_container.delete('text'+str(thread.ident))
        lock_container.delete('acquireImage'+str(thread.ident))
        height = container_data[3]+((80/100)*self.containerHeight)
        orient = container_data[4]
        wait_data= container_data[1]
        wait_data.drawFutureAcquireThread()
        tag = "release"+str(thread.ident)
        if orient== Controller.SINISTRA:
            self.primaryCanvas.create_image((5/100)*self.primaryCanvas.winfo_width(),height,tag = 'inactiveimage'+str(thread.ident),image=self.computerImage,anchor='n')
            self.primaryCanvas.create_text((5/100)*self.primaryCanvas.winfo_width(),height+70,text = thread.getName(),tag=tag,anchor='n')
        else:
            self.primaryCanvas.create_image((95/100)*self.primaryCanvas.winfo_width(),height,tag = 'inactiveimage'+str(thread.ident),image=self.computerImage,anchor='n')
            self.primaryCanvas.create_text((95/100)*self.primaryCanvas.winfo_width(),height+70,text = thread.getName(),tag=tag,anchor='n')
        startTime = time.time()
        lock_container.itemconfigure('greyRedSem',state="normal")
        self.releasingLock.append(lock)
        lock_container.after(500,self.__blinkLock,lock_container,True,lock)
        self.__moveFromLockToInactive(tag,thread,orient,startTime,lock,wait_data,lock_container)
        sleepTime = (height+(self.primaryCanvas.winfo_width()/2)-((30/100)*self.primaryCanvas.winfo_width()))/80
        return sleepTime
        
        #lock_container.itemconfigure('redSem',state="normal") 

    def notifyLock(self,lock):
        container_data = self.lockContainer[lock]
        conditionContainer = container_data[2]
        startTime = time.time()
        red = True
        self.__blinkCondition(conditionContainer,startTime,red)
    
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
        
        self.window.after(50,self.update)
    
    def start(self):
        ##print("Number of lock: ",len(self.containers))
        height = self.containerHeight*len(self.lockContainer)*3
        self.primaryCanvas.configure(height=height)
       
        '''
        for key in self.lockContainer.keys():
            canvas_data = self.lockContainer[key]
            canvas = canvas_data[0]
            wait_container = canvas_data[1]
            orient = canvas_data[3]
            relX = 0.2 if orient == Controller.SINISTRA else 0.8
            canvas.place(relx=relX,y=canvas_data[2],anchor='n')
            wait_container.place(relx=0.5,anchor='center',rely=0.25, relheight=0.50,relwidth=1)

        for scroll in self.scrolls:
            scroll.place(relx=1,rely=0.5,relheight=1,anchor='e')

        '''

        self.window.after(50,self.update)
        self.window.mainloop()

    def __onclose(self):
        self.window.destroy()
        for thread in self.threads:
            thread.exit()
 
    
controller = Controller()

class _StopAndPlay:
    def __init__(self):
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.running=True
    
    def stop(self):
        with self.lock:
            self.running=False
    
    def play(self):
        with self.lock:
            self.running = True
            self.condition.notifyAll()
    
    def run(self):
        with self.lock:
            while not self.running:
                self.condition.wait()
class GraphLock:
    __id = 1
    def __init__(self):
        self.id = GraphLock.__id
        GraphLock.__id+=1
        self.controller=controller
        self.controller.addLock(self)
        
        self.waitLock = Lock()
        self.lock = Lock()
        self.canAcquire=False
        self.isReleased = False
        self.isInWait = False
        self.releaseLock=Lock()
        self.releaseCondition = Condition(self.releaseLock)        
        self.waitCondition = Condition(self.waitLock)
        
        self.lockCondition=Lock()
        self.condCondition=Condition(self.lockCondition)

        self.condionThread=[]
        self.playController = _StopAndPlay()

    def acquire(self):
        
        self.playController.run()
        self.waitLock.acquire()
        #print('\nwait lock ',self.id, current_thread().getName())
        self.isReleased=False
        sleepTime = self.controller.setWaitThread(current_thread(),self)
        sleep(sleepTime)
        self.waitLock.release()
        self.playController.run()
        ###print(current_thread().getName()," have released")
        self.lock.acquire()
        ##print('ACQUIRE LOCK ',self.id, current_thread().getName(),'\n')
        sleep(2)
        self.controller.setAcquireThread(current_thread(),self)
        sleep(3)
    
    def release(self):
        self.playController.run()

        self.releaseLock.acquire()
        if current_thread() in self.condionThread:
            self.condionThread.remove(current_thread())
            print('in release condition')
            self.controller.setAcquireThreadFromCondition(current_thread(),self)
            sleep(3)

        self.controller.setReleaseThread(current_thread(),self)
        while not self.isReleased :
            self.releaseCondition.wait()
        self.releaseLock.release()
        ##print('released lock ',self.id, current_thread().getName())
        self.isReleased = False
        self.lock.release()
        sleep(2)
    
    def addConditionThread(self,thread):
        self.playController.run()
        self.controller.setThreadInCondition(thread,self)
        self.condionThread.append(thread)
    
    def notifyForLock(self):
        pass
    
    def getId(self):
        return self.id


class GraphThread(Thread):
    def __init__(self):
        ###print('ok init graphthread')
        super().__init__()
        self.controller=controller
        self.controller.addThread(self)
    
    def exit(self):
        os._exit(0)        
        

class GraphCondition(threading.Condition):
    def __init__(self,glock):
        super().__init__(glock.lock)
        self.glock = glock
        self.controller=controller
    
    def wait(self):
        self.glock.addConditionThread(current_thread())
        super().wait()
    
    def notifyAll(self):
        self.controller.notifyLock(self.glock)
        super().notifyAll()

def startGraph():
    controller.start()
    

