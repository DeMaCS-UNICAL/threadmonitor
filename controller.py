from tkinter import *
import tkinter
from threading import Lock,Thread
from PIL import ImageTk
import os
import threading

class Controller:
    FINISH=False
    def __init__(self):
        
        ### Variabili che indicano gli eventuali cambiamenti ###
        self.readyChanges=False
        self.waitingChanges=False

        ### Dizionario che associa a ogni thread il relativo canvas ###
        self.threads={}

        self.objectThreads=[]

        self.waiting=[]

        ### Variabile che contiene il nome del thread che possiede il lock ###
        self.ready=""

        self.window=Tk()


        self.screen_width=800
        self.screen_heigth=self.window.winfo_screenheight()
        self.pad = 3
        self.window.geometry('{0}x{1}'.format(self.screen_width-self.pad,self.screen_heigth-self.pad))
        
        ### Scroll verticale ###
        self.yscroll = Scrollbar(self.window, orient=VERTICAL)
        self.yscroll.pack(side=RIGHT,fill=Y)

        ### Associazione dello scroll al canvas principale ###
        self.canvas=Canvas(self.window)
        self.canvas.pack(fill=BOTH, expand=True)

        self.canvas['yscrollcommand']= self.yscroll.set
        self.yscroll['command']= self.canvas.yview

        ### Frame che conterrà tutti i canvas relativi ai threads ###
        self.frame = Frame(self.canvas)

        self.canvas.create_window(self.screen_width, self.screen_heigth, window=self.frame, anchor='nw') # Canvas equivalent of pack()

        ### Background dei canvas relativi ai threads ###
        self.background = ImageTk.Image.open('resource/backgroundCanvas.png')
        self.background = self.background.resize((self.screen_width,int((30/100)*self.screen_heigth)))
        self.background = ImageTk.PhotoImage(master=self.canvas,image=self.background)
        
        ### Immagine che rappresenta un thread ###
        self.computerImage = ImageTk.Image.open('resource/computer.png')
        self.computerImage = self.computerImage.resize((70,70))
        self.computerImage = ImageTk.PhotoImage(master=self.canvas,image=self.computerImage)
        
        ### Variabili che salvano la reference alle immagini create dal canvas ###        
        self.backgroundObjFromWindows=''
        self.computerObjFromWindows=''
        
        self.window.title('Test')
        #self.canvas.create_window(1, 1, window=self.frame, anchor='nw') 

        '''
        self.window.after(50,self.update)
        self.window.mainloop()
        '''
        

    def addThread(self,threads):
        self.objectThreads=threads
        for t in threads:
            self.threads[t.getName()]=Canvas(self.frame,width=self.screen_width,height=int((30/100)*self.screen_heigth),bg='gray')
        
        '''
        tcanvas = Canvas(self.frame,width=self.screen_width,height=int((30/100)*self.screen_heigth),bg='gray')
        self.threads[thread.getName()]=tcanvas
        self.backgroundObjFromWindows=tcanvas.create_image(0,0,image=self.background,anchor=NW,tags='back')
        self.computerObjFromWindows=tcanvas.create_image(int((self.screen_width/3)/2),int(((self.screen_heigth-((11/100)*self.screen_heigth))/3)/3),image=self.computerImage,anchor=NW,tags='comp')
        self.threads[thread.getName()].pack()
        '''
        
        
    
    def start(self):
        
        for thread in self.threads.keys():
            canvas=self.threads[thread]
            self.backgroundObjFromWindows=canvas.create_image(0,0,image=self.background,anchor=NW,tags='back')
            self.computerObjFromWindows=canvas.create_image(int((self.screen_width/3)/2),int(((self.screen_heigth-((11/100)*self.screen_heigth))/3)/3),image=self.computerImage,anchor=NW,tags='comp')
            canvas.create_text(60,20,text=thread, font=('Fixedsys',18,'italic'))

            canvas.pack()
        
        
        self.window.title('Test')
        self.canvas.create_window(1, 1, window=self.frame, anchor='nw') 

        self.window.after(50,self.update)
        self.window.protocol('WM_DELETE_WINDOW',self.__onclose)
        self.window.mainloop()
        
     
        
    def setThreadWithLock(self,thread_id):
        
        self.readyChanges=True        
        print('Entrato in cambia testo')
        self.ready="Lock preso da "+thread_id
        if thread_id in self.waiting:
            print(thread_id+' present in waiting')
            self.waiting.remove(thread_id)
            self.waitingChanges=True
            canvas = self.threads[thread_id]
            self.__moveToAcquire(canvas)
        print('fine cambia testo')
        
        
    def addWaitThread(self,thread_name):
        if thread_name not in self.waiting:
            self.waiting.append(str(thread_name))
            self.waitingChanges=True
            canvas = self.threads[thread_name]
            self.__moveToWait(canvas)
            print(self.waiting)
        
    def releaseThread(self,thread_name):
        canvas = self.threads[thread_name]
        self.__moveToInactive(canvas)
    def update(self):

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))    
        self.window.after(100,self.update)

    def __moveToWait(self,canvas):
        try:
            x=canvas.coords('comp')[0]
            if x<400:
                canvas.move('comp',10,0)
                canvas.after(30,self.__moveToWait,canvas)
        except:
            pass



    def __moveToAcquire(self,canvas):
        try:
            x=canvas.coords('comp')[0]
            if x<700:
                canvas.move('comp',10,0)
                canvas.after(30,self.__moveToAcquire,canvas)
        except:
            pass

    def __moveToInactive(self,canvas):
        try:
            x=canvas.coords('comp')[0]
            if x>int((self.screen_width/3)/2):
                canvas.move('comp',-10,0)
                canvas.after(30,self.__moveToInactive,canvas)
        except:
            pass


    def __onclose(self):
        self.window.destroy()
        Controller.FINISH=True
        