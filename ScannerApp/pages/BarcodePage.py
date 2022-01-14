import tkinter as tk
from threading import Thread
from . import BaseViewPage

class BarcodePage(BaseViewPage):
    resultType = lambda x:'Not Scanned'
    def __init__(self, parent, master):
        
        self.validationStatus = []
        super().__init__(parent,master)        
        self.offset = -160
        self.camera = master.camera
        self.createDefaultWidgets()
        self.placeDefaultWidgets()
        self.create_widgets()
        self.initKeyboard()
        self.state = ['validationStatus', ]
        if not self.master.devMode:
            self.disableNextBtn()
    
    def placeDefaultWidgets(self):
        
        self._msg.place(x=20, y=430, width=740)
        
        self._prevBtn.place(x=340 , y=300,  height=90 ,width=130,)
        self._nextBtn.place(x=650 , y=300, height=90, width=130)
        self._title.place(x= 0,y=20,width= 800,height=30)

    def create_widgets(self):
        self.scanVar = tk.StringVar()
        # self.scanVar1.set('1234567890')
        self.scan = tk.Label(
            self, textvariable=self.scanVar, font=('Arial', 35))
        l1 = tk.Label(self, text='ID:', font=('Arial', 35)
                 )
        self.scan.place(x=460+self.offset, y=110)  # grid(column=1,row=0,)
        l1.place(x=340 + self.offset, y=110)
       
    def showPage(self,title='Default Barcode Page',msg="Scan Barcode on plate",color='black'):
        self.setTitle(title,color)
        self.keySequence = []
        self.tkraise()
        self.focus_set()     
        self.displaymsg(msg)
        self.showPrompt()

    def closePage(self):
        if not self.master.devMode:
            self.disableNextBtn()
        self.keySequence = []

    def resetState(self):
        self.result  = self.resultType()
        self.scanVar.set("")
        if not self.master.devMode:
            self.disableNextBtn()
    
    def scanlistener(self,e):
        char = e.char
        if char.isalnum():
            self.keySequence.append(char)
            self.scanVar.set(''.join(self.keySequence))        
        else:
            if self.keySequence:
                self.keyboardCb(''.join(self.keySequence))
            self.keySequence=[]
        #return 'break' to stop keyboard event propagation.
        return 'break'

    def keyboardCb(self,code):
        self.result = code
        self.validationStatus = self.master.currentRoutine.validateResult(code)
        self.showPrompt()
        
    def showPrompt(self):
        code = self.result
        self.scanVar.set(code)
        if code == "Not Scanned":
            self.scan.config(fg='black')
            return
        valid,msg,bypass = self.validationStatus
        if valid:
            self.result = code
            self.scan.config(fg='green')
            self.displaymsg(msg,'green')
            self.enableNextBtn()
        else:
            self.scan.config(fg='red')
            self.displaymsg(msg, 'red')
            if bypass:
                self.enableNextBtn()
            else:
                self.disableNextBtn()