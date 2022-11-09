import logging
import tkinter as tk
from ..utils.logger import Logger
from ..utils import warnImplement
import time
from datetime import datetime

class BaseViewPage(tk.Frame,Logger):
    resultType = str # the type of result this page will create.
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        Logger.__init__(self,self.__class__.__name__,
        logLevel=self.master.LOGLEVEL,
        fileHandler=self.master.fileHandler)

        # self.result is used to store page result. this result is passed to routine.validateResult.
        self.result = self.resultType()
        self._info = None
        self.state=[]   

    def createDefaultWidgets(self):
        "creat title, prev and next button,msg box"
        self._msgVar = tk.StringVar()
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))
        self._titleVar = tk.StringVar()
        self._title = tk.Label(self,textvariable=self._titleVar, font=("Arial",20))
        self._prevBtn = tk.Button(self,text='Prev',font=('Arial',32),command=self.prevPageCb)
        self._nextBtn = tk.Button(self,text='Next',font=('Arial',32),command=self.nextPageCb)
        
    def placeDefaultWidgets(self):
        self._msg.place(x=20, y=430, width=740)
        self._prevBtn.place(x=340, y=300,  height=90 ,width=130,)
        self._nextBtn.place(x=650, y=300, height=90, width=130)
        self._title.place(x=340,y=20,width=440,height=30)

    def resetState(self):
        warnImplement('resetState',self)
        self.result  = self.resultType()
    
    def showPage(self,*args,**kwargs):
        warnImplement('showPage',self)
       
        self.tkraise()
        self.focus_set()
    
    def closePage(self):
        warnImplement('closePage',self)

         
    def setTitle(self,title,color='black'):
        self._titleVar.set(title)
        if color:
            self._title.config(fg=color)

    def readResultState(self):
        return self.result, {i:getattr(self,i) for i in self.state}

    def setResultState(self,result,state):
        self.result = result
        for k,i in state.items():
            setattr(self,k,i)
    
    def prevPageCb(self):
        "return to previous page in the current routine"
        self.master.currentRoutine.prevPage()
    
    def enableNextBtn(self):
        self._nextBtn['state'] = 'normal'
    def disableNextBtn(self):
        self._nextBtn['state'] = 'disabled'
    
    def nextPageCb(self):
        self.master.currentRoutine.nextPage()

    def displaymsg(self, msg, color='black'):
        self._msgVar.set(msg)
        if color:
            self._msg.config(fg=color)
    
    def displayInfo(self,info):
        self._info.configure(state='normal')
        self._info.insert('1.0',info+'\n')
        self._info.configure(state='disabled')
    
    def clearInfo(self):
        "clear scrolledtext"
        self._info.configure(state='normal')
        self._info.delete('1.0',tk.END)
        self._info.configure(state='disabled')

    def initKeyboard(self,type='default',lag=1):        
        if type=='lag':
            self.bind("<Key>",self.lagsScanListener(lag))
        else:            
            self.bind("<Key>",self.scanlistener)
        self.keySequence = []

    def scanlistener(self,e):      

        logging.warning('BaseViewPage > scanlistener > e.char: %s',e.char)

        """
        this scan listener only accept alphanumeric values.
        """ 
        char = e.char       
        if char=='\r':
            if self.keySequence:
                self.keyboardCb(''.join(self.keySequence))
            self.keySequence=[]            
        else:
            self.keySequence.append(char)
        #return 'break' to stop keyboard event propagation.
        return 'break'
    
    def lagsScanListener(self,lag=0.5):
        "produce scanlistener that lag for less than lag time. in seconds"
        def cb(e):        
            char = e.char
            if time.time() - self.lastInputTime > lag:
                # if the last input is more than 1 seconds ago, reset keySequence.
                self.keySequence=[]
            if char=='\r':
                if self.keySequence:
                    self.keyboardCb(''.join(self.keySequence))
                self.keySequence=[]            
            else:
                self.keySequence.append(char)
            self.lastInputTime = time.time()
            #return 'break' to stop keyboard event propagation.
            return 'break'
        return cb

    def keyboardCb(self,code):
        warnImplement('keyboardCb',self)
