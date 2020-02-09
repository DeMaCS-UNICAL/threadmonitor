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




class _InactiveContainer:
    def __init__(self,inactiveContainer,image):
        self.container = inactiveContainer
        self.lock = Lock()
        self.inactiveThreads = []
        self.currentWidth = 0
        self.image = image

    def addThreadInactive(self,thread_name,lock):
        with self.lock:
            self.inactiveThreads.append(thread_name)
            #print("Add thread inactive ",thread_name)
            self.drawNewThread(thread_name,lock)

    def removeThreadInactive(self,thread_name):
        with self.lock:
            if thread_name in self.inactiveThreads:
                for thread in self.inactiveThreads:
                    self.container.delete('image'+thread)
                    self.container.delete(thread)
                self.inactiveThreads.remove(thread_name)
                #print(self.inactiveThreads)
                self.redrawThread()
    
    def redrawThread(self):
        currentWidth = 0
        

        for thread in self.inactiveThreads:
            tag=thread
            self.container.create_image(currentWidth,0,image=self.image,tag='image'+tag,anchor='n')
            self.container.create_text(currentWidth,70,text=thread,tag=tag,anchor="n")
            currentWidth+=100
        self.currentWidth=currentWidth
    
    def drawNewThread(self,thread_name,lock):
        lock.releaseLock.acquire()
        tag = thread_name
        self.container.create_image(self.currentWidth,0,image=self.image,tag='image'+tag,anchor='n')
        self.container.create_text(self.currentWidth,70,text=thread_name,tag=tag,anchor="n")
        self.currentWidth +=100
        lock.releaseCondition.notify_all()
        lock.isReleased=True
        print('release lock draw ',lock.getId(), current_thread().getName())
        lock.releaseLock.release()



class _WaitContainer:
    def __init__(self,wait_container,image):
        self.container = wait_container
        self.lock = Lock()
        self.waitThreads = []
        self.currentHeight = 0
        self.image = image
    
    def addThreadInWait(self,thread_name,lock):
        with self.lock:
            self.waitThreads.append(thread_name)
            #print("Add thread ",thread_name)
            self.drawNewThread(thread_name)
            lock.canAquire=True
            #print('acquired')

    def removeThreadInWait(self,thread_name):
        with self.lock:
            #print(self.waitThreads)
            for thread in self.waitThreads:
                self.container.delete(thread)
                self.container.delete('image'+thread)
            self.waitThreads.remove(thread_name)
            self.redrawThread()
    
    def redrawThread(self):
        currentHeight = 0
        

        for thread in self.waitThreads:
            tag=thread
            self.container.create_image(int(self.container.winfo_width()/2),currentHeight,image=self.image,tag='image'+thread,anchor='n')
            currentHeight+=70
            self.container.create_text(int(self.container.winfo_width()/2),currentHeight,text=thread,tag=tag,anchor="n")
            currentHeight+=20
        self.currentHeight=currentHeight
    
    def drawNewThread(self,thread_name):
        tag = thread_name
        self.container.create_image(int(self.container.winfo_width()/2),self.currentHeight,image=self.image,tag='image'+thread_name,anchor='n')
        self.currentHeight+=70
        self.container.create_text(int(self.container.winfo_width()/2),self.currentHeight,text=thread_name,tag=tag,anchor="n")
        self.currentHeight +=20



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
        self.currentHeightPosition = 50
        self.containerWidth = self.screen_width/5
        self.containerHeight = self.screen_heigth/3
        
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


        
        ##print(self.primaryCanvas.winfo_screenmmwidth())
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
        self.primaryCanvas=Canvas(self.frame,background='grey',highlightthickness=0, highlightbackground="black",height=10000,width=self.screen_width)
        self.window.update_idletasks()
        self.yscroll = Scrollbar(self.frame, orient=VERTICAL)
        self.yscroll['command']= self.primaryCanvas.yview
        self.yscroll.pack(side=RIGHT,fill=Y)
        self.primaryCanvas['yscrollcommand']= self.yscroll.set
        self.primaryCanvas.pack(fill=BOTH,expand=True)

        self.inactiveCanvas=Canvas(self.primaryCanvas,background='red',highlightthickness=1, highlightbackground="black",height=100,width=300)
        self.inactiveScroll = ttk.Scrollbar(self.inactiveCanvas,orient=HORIZONTAL,command=self.inactiveCanvas.xview)
        self.inactiveScroll.place(relx=0.5,rely=0.9,width=305,anchor='center')
        self.inactiveCanvas.configure(xscrollcommand=self.inactiveScroll.set)
        #self.inactiveCanvas.pack(anchor='center',pady=10)
        self.primaryCanvas.create_window(self.screen_width/2,0,window=self.inactiveCanvas,anchor='center')

        ### Inizializzazioni immagini ###
        self.computerImage = ImageTk.Image.open('resource/computer.png')
        self.computerImage = self.computerImage.resize((70,70))
        self.computerImage = ImageTk.PhotoImage(master=self.primaryCanvas,image=self.computerImage)
        
        self.background = ImageTk.Image.open('resource/background.jpg')
        self.window.after(50,self.update)

        self.inactiveData = _InactiveContainer(self.inactiveCanvas,self.computerImage)

    

    def addThread(self,thread):
        self.threads.append(thread)
        #self.inactiveData.addThreadInactive(thread.getName())

    def addLock(self,lock):
        ### creo il container e lo aggiungo alla lista di container ###
        
        container=Canvas(self.primaryCanvas,background='white',highlightthickness=1, highlightbackground="black",height=self.containerHeight,width=self.containerWidth)
        
        
        self.containers.append(container)
        relX = (20/100)*self.screen_width if self.currentOrientPosition%2 == 0 else (80/100)*self.screen_width
        self.primaryCanvas.create_window(relX,self.currentHeightPosition,window=container,anchor='n')#container.place(relx=relX,y=self.currentHeightPosition,anchor='n')

        
        ### creo il container per i thread in wait ###
        waitContainer= Canvas(container,background='yellow',highlightthickness=1, highlightbackground="black",width=self.containerWidth,height=int(self.containerHeight/2))
        container.create_window(self.containerWidth/2,(25/100)*self.containerHeight,window=waitContainer,anchor='center')#.place(relx=0.5,anchor='center',rely=0.25, relheight=0.50,relwidth=1)
        self.waitContainer[lock]=waitContainer

        
        ### creo il relativo scroll ###
        scroll = Scrollbar(waitContainer,orient=VERTICAL,command=waitContainer.yview)
        scroll.place(relx=1,rely=0.5,relheight=1,anchor='e')
        waitContainer.configure(yscrollcommand=scroll.set)
        self.scrolls.append(scroll)
        
        wait_data = _WaitContainer(waitContainer,self.computerImage)
     

        ### associo al lock il relativo container ###
        self.lockContainer[lock]=[container,wait_data,self.currentHeightPosition,self.currentOrientPosition%2]
        
        ### aggiorno le variabili per il posizionamento ###
        self.currentOrientPosition+=1
        if(self.currentOrientPosition%2 == 0):
            self.currentHeightPosition+=self.containerHeight+30
        
    def __moveFromInactiveToWait(self,thread,wait_container,height,orient,tag,lock,startTime):
       
        if self.primaryCanvas.coords(tag)[1]<=height:
            self.primaryCanvas.move('image'+thread,0,2)
            self.primaryCanvas.move(tag,0,2)
            self.primaryCanvas.after(6,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)

                
        else:
            if orient == Controller.SINISTRA:
                if self.primaryCanvas.coords(tag)[0]>=((20/100)*self.primaryCanvas.winfo_width()):
                    self.primaryCanvas.move(tag,-2,0)
                    self.primaryCanvas.move('image'+thread,-2,0)
                    self.primaryCanvas.after(10,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)
                else:
                    #wait_container.create_text(int(wait_container.winfo_width()/2),0,text=thread,tag=tag,anchor="n")
                    endTime = time.time()
                    #print('Time is: ',endTime-startTime, '\nHeight is: ',height,'\nWidth is: ',self.primaryCanvas.winfo_width(),'\nCoords of thread is: ',self.primaryCanvas.coords(tag))
                    wait_container.addThreadInWait(thread,lock)
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('image'+thread)


            else:
                if self.primaryCanvas.coords(tag)[0]<=((80/100)*self.primaryCanvas.winfo_width()):
                    self.primaryCanvas.move(tag,2,0)
                    self.primaryCanvas.move('image'+thread,2,0)
                    self.primaryCanvas.after(10,self.__moveFromInactiveToWait,thread,wait_container,height,orient,tag,lock,startTime)
                else:
                    #wait_container.create_text(int(wait_container.winfo_width()/2),0,text=thread,tag=tag,anchor="n")
                    endTime = time.time()
                    ##print('Time is: ',endTime-startTime, '\nHeight is: ',height,'\nWidth is: ',self.primaryCanvas.winfo_width())
                    wait_container.addThreadInWait(thread,lock)
                    lock.canAcquire=True
                    self.primaryCanvas.delete(tag)
                    self.primaryCanvas.delete('image'+thread)

    def __moveFromLockToInactive(self,tag,thread,orient,startTime,lock):
        
        if self.primaryCanvas.coords(tag)[1]>self.inactiveCanvas.winfo_y()+30:
            self.primaryCanvas.move(tag,0,-3)
            self.primaryCanvas.move('inactiveimage'+thread,0,-3)
            self.primaryCanvas.after(12,self.__moveFromLockToInactive,tag,thread,orient,startTime,lock)
        else:
            if orient == Controller.DESTRA and self.primaryCanvas.coords('inactiveimage'+thread)[0]>=((50/100)*self.screen_width):# and (self.primaryCanvas.coords('inactiveimage'+thread)[0]<=(50/100)*self.screen_width):                    self.primaryCanvas.move(tag,1,0)
                self.primaryCanvas.move('inactiveimage'+thread,-2,0)
                self.primaryCanvas.move(tag,-2,0)
                self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,startTime,lock)
            elif orient == Controller.SINISTRA and self.primaryCanvas.coords('inactiveimage'+thread)[0]<=((50/100)*self.screen_width):# and self.primaryCanvas.coords('inactiveimage'+thread)[0]>=(50/100)*self.screen_width:                    self.primaryCanvas.move(tag,1,0)
                self.primaryCanvas.move('inactiveimage'+thread,2,0)
                self.primaryCanvas.move(tag,2,0)
                self.primaryCanvas.after(10,self.__moveFromLockToInactive,tag,thread,orient,startTime,lock)
            else:
                self.primaryCanvas.delete(tag)
                self.primaryCanvas.delete('inactiveimage'+thread)
                self.inactiveData.addThreadInactive(thread,lock)
                endTime = time.time()
                #print('Release time is: ',endTime-startTime)


    def setWaitThread(self,thread,lock):
        
        container_data = self.lockContainer[lock]
        

        wait_data = container_data[1]
        
        #if wait_container
        height = container_data[2]+((30/100)*self.containerHeight)
        orient = container_data[3]
        tag="wait"+thread+str(lock.getId())
        
        self.primaryCanvas.create_text(int(self.primaryCanvas.winfo_width()/2),70,text=thread,tag=tag,anchor="n")
        self.primaryCanvas.create_image(int(self.primaryCanvas.winfo_width()/2),0,image=self.computerImage,tag='image'+thread,anchor='n')
        timeStart = time.time()
        self.__moveFromInactiveToWait(thread,wait_data,height,orient,tag,lock,timeStart)
        self.inactiveData.removeThreadInactive(thread)

        sleepTime = (height+(self.primaryCanvas.winfo_width()/2)-((30/100)*self.primaryCanvas.winfo_width()))/100 
        return sleepTime
    
    def setAcquireThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        #print('Acquire lock from ',lock.getId())
        lock_container = container_data[0]
        tag=thread
        
        wait_container = container_data[1]
        wait_container.removeThreadInWait(thread)
        lock_container.create_image((50/100)*self.containerWidth,(60/100)*self.containerHeight,tag = 'acquireImage'+thread,image=self.computerImage,anchor='n')
        lock_container.create_text((50/100)*self.containerWidth,(90/100)*self.containerHeight,text=thread,tag=tag,anchor='n',fill='green')
    
    def setReleaseThread(self,thread,lock):
        container_data = self.lockContainer[lock]
        lock_container=container_data[0]
        lock_container.delete(thread)
        lock_container.delete('acquireImage'+thread)
        height = container_data[2]+((80/100)*self.containerHeight)
        orient = container_data[3]

        tag = "release"+thread
        if orient== Controller.SINISTRA:
            self.primaryCanvas.create_image((5/100)*self.primaryCanvas.winfo_width(),height,tag = 'inactiveimage'+thread,image=self.computerImage,anchor='n')
            self.primaryCanvas.create_text((5/100)*self.primaryCanvas.winfo_width(),height+70,text = thread,tag=tag,anchor='n')
        else:
            self.primaryCanvas.create_image((95/100)*self.primaryCanvas.winfo_width(),height,tag = 'inactiveimage'+thread,image=self.computerImage,anchor='n')
            self.primaryCanvas.create_text((95/100)*self.primaryCanvas.winfo_width(),height+70,text = thread,tag=tag,anchor='n')
        startTime = time.time()
        self.__moveFromLockToInactive(tag,thread,orient,startTime,lock)
        sleepTime = (height+(self.primaryCanvas.winfo_width()/2)-((30/100)*self.primaryCanvas.winfo_width()))/80
        return sleepTime 


    def update(self):
        self.primaryCanvas.configure(scrollregion=self.primaryCanvas.bbox("all"))
        self.inactiveCanvas.configure(scrollregion=self.inactiveCanvas.bbox("all"))
                
        for key in self.waitContainer.keys():
            self.waitContainer[key].configure(scrollregion=self.waitContainer[key].bbox("all"))
        
        self.window.after(50,self.update)
    
    def start(self):
        #print("Number of lock: ",len(self.containers))
        height = self.containerHeight*len(self.lockContainer)
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
        
    
controller = Controller()

class GraphLock:
    __id = 1
    def __init__(self):
        self.controller=controller
        self.controller.addLock(self)
        self.id = GraphLock.__id
        GraphLock.__id+=1
        self.waitLock = Lock()
        self.lock = Lock()
        self.canAcquire=False
        self.isReleased = False
        self.isInWait = False
        self.releaseLock=Lock()
        self.releaseCondition = Condition(self.releaseLock)        
        self.waitCondition = Condition(self.waitLock)

    def acquire(self):
        self.waitLock.acquire()
        print('\nwait lock ',self.id, current_thread().getName())

        self.isReleased=False
        sleepTime = self.controller.setWaitThread(current_thread().getName(),self)
        sleep(sleepTime)
        self.waitLock.release()
        ##print(current_thread().getName()," have released")
        self.lock.acquire()
        print('ACQUIRE LOCK ',self.id, current_thread().getName(),'\n')

        self.controller.setAcquireThread(current_thread().getName(),self)
    
    def release(self):
        self.releaseLock.acquire()
        self.controller.setReleaseThread(current_thread().getName(),self)
        while not self.isReleased :
            print(current_thread().getName(),'sta aspettando sul lock ',self.id)
            self.releaseCondition.wait()
        self.releaseLock.release()
        print('released lock ',self.id, current_thread().getName())
        self.isReleased = False
        self.lock.release()
        sleep(2)
    def getId(self):
        return self.id

class GraphThread(Thread):
    def __init__(self):
        ##print('ok init graphthread')
        super().__init__()
        self.controller=controller
        self.controller.addThread(self)
    
    def exit(self):
        os._exit(0)        


def startGraph():
    controller.start()
    

