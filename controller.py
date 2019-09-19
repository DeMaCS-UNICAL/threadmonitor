from tkinter import *
import tkinter
from threading import Lock,Thread
class Controller:
    def __init__(self):
        #tkinter.NoDefaultRoot()
        self.readyChanges=False
        self.waitingChanges=False
        self.threads=[]
        self.window=Tk()
        
        self.screen_width=self.window.winfo_screenwidth()
        self.screen_heigth=self.window.winfo_screenheight()
        
        
        self.canvas=Canvas(self.window,width=self.screen_width,height=self.screen_heigth)
        
        self.readyFrame=Frame(self.window,bg="green")
        self.readyFrame.pack(side="top", fill="both", expand=True)
        self.label=Label(self.readyFrame,text='test')
        self.label.pack(side=TOP)
        self.waitFrame=Frame(self.window,bg="yellow")
        self.waitFrame.pack(side="bottom", fill="both", expand=True)
        
        
        self.label.grid(column=0, row=0)
        self.waiting=[]
        self.ready=""
        self.refresh = Thread(target=self.update())
        
    
    def addThread(self,thread):
        self.threads.append(thread.getName())
    
    def start(self):
        self.refresh.start()
        self.window.title('Test')
        self.window.geometry('1080x1920')
        self.window.mainloop()
     
        
    def setThreadWithLock(self,thread_id):
        self.readyChanges=True        
        print('Entrato in cambia testo')
        self.ready="Lock preso da "+thread_id
        if thread_id in self.waiting:
            print(thread_id+' present in waiting')
            self.waiting.remove(thread_id)
            self.waitingChanges=True
        print('fine cambia testo')
        
    def addWaitThread(self,thread_name):
        if thread_name not in self.waiting:
            self.waiting.append(str(thread_name))
            self.waitingChanges=True
            print(self.waiting)
        
        
    def update(self):
        if self.readyChanges:
            self.label.configure(text=self.ready)
            self.readyChanges=False
        if self.waitingChanges:
            for widget in self.waitFrame.winfo_children():
                widget.destroy()
            roww=1
            
            for th in self.waiting:
                label = Label(self.waitFrame,text=th+' WAIT')
                label.pack(side=BOTTOM)
                
                
            self.waitingChanges=False
            
        self.window.after(100,self.update)
