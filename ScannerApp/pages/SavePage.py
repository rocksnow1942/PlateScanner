import tkinter as tk
from threading import Thread
from . import BaseViewPage


class SavePage(BaseViewPage):
    def __init__(self, parent, master):
        super().__init__(parent, master)
        self.create_widgets()
    
    def create_widgets(self):
        self._msgVar = tk.StringVar()
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))
        self._titleVar = tk.StringVar()
        self._title = tk.Label(self,textvariable=self._titleVar, font=("Arial",20))
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',32),command=self.prevPageCb)
        self.saveBtn = tk.Button(self,text='Save',font=('Arial',32),command=self.saveCb)
        scbar = tk.Scrollbar(self,)
        self._info = tk.Text(self,font=('Arial',16),padx=3,yscrollcommand=scbar.set)
        scbar.config(command=self._info.yview)
        self._title.place(x=40,y=20,width=720,height=30)
        self._info.place(x=40,y=80,width=720,height=190)
        scbar.place(x = 760,y=80,width=20,height=190)
        self._prevBtn.place(x=80, y=300,  height=90 ,width=130,)
        self.saveBtn.place(x=590, y=300, height=90, width=130)
        self._msg.place(x=20, y=430, width=740)

    def closePage(self):
        self.clearInfo()
        

    def resetState(self):
        self.clearInfo()
        self._prevBtn['state'] = 'normal'
        self.saveBtn['state'] = 'normal'
        self.displaymsg("")

        
    def showPage(self,title="Default Save Result Page",msg='Check the result and click save.',color='black'):
        self.setTitle(title,color)        
        self.displayInfo(self.master.currentRoutine.displayResult())
        self.displaymsg(msg)
        self.tkraise()
        self.focus_set()        
        
        
    def saveCb(self):
        def save():
            try:
                for p in self.master.currentRoutine.saveResult():
                    self.displayInfo(p)
            except Exception as e:
                self.error(f"SavePage.saveCb error: {e}")
                self.displaymsg(f'Error in saving: {str(e)[0:40]}','red')
            self._prevBtn['state'] = 'normal'
            self.saveBtn['state'] = 'normal'
        Thread(target=save,).start()
        self.displaymsg('Saving results...','green')
        self._prevBtn['state'] = 'disabled'
        self.saveBtn['state'] = 'disabled'
